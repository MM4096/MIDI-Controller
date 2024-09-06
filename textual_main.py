import multiprocessing
from pathlib import PosixPath
import threading
from queue import Queue

import mido
from textual import on, events
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.screen import Screen, ModalScreen
from textual.widget import AwaitMount
from textual.widgets import Header, Footer, Static, Label, Button, Input, ListView, DirectoryTree, ListItem
from textual.app import App, ComposeResult

from modules import preferences, patcher
from modules.tools import is_recognized_boolean, convert_string_to_boolean, sort_list_by_numbering_system
from modules import file_manager


#region helper functions
def create_needed_files():
	file_manager.create_dir_if_not_exists(file_manager.get_user_data_dir())
	file_manager.create_dir_if_not_exists(file_manager.get_user_data_dir() + "/patches")
	file_manager.create_dir_if_not_exists(file_manager.get_user_data_dir() + "/presets")
	file_manager.create_dir_if_not_exists(file_manager.get_user_data_dir() + "/temp")
	new_preferences = preferences.update_preferences()

def get_main_port():
	with open(file_manager.get_user_data_dir() + "/main_port.data", "r") as f:
		return f.read()

#endregion


class OrderableListWidget(Static):
	BINDINGS = [
		("plus", "move_item_up", "Move Selected Item Up"),
		("minus", "move_item_down", "Move Selected Item Down"),
		("backspace", "delete_item", "Delete Selected Item"),
	]

	CSS_PATH = "css/orderable_list.tcss"

	list_items: list = []

	def __init__(self, items: list):
		super().__init__()
		self.list_items = items

	def compose(self) -> ComposeResult:
		yield Vertical(
			ListView (
				id="orderable_list",
			),
			Horizontal (
				Button("Move Up", id="move_up"),
				Button("Move Down", id="move_down"),
				Button("Delete", id="delete"),
				id="orderable_list_buttons",
			),
		)


	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "move_up":
			self.action_move_item_up()
		elif event.button.id == "move_down":
			self.action_move_item_down()
		elif event.button.id == "delete":
			self.action_delete_item()


	def redraw(self):
		list_view = self.query_one("#orderable_list")
		list_view.remove_children()
		for item in self.list_items:
			list_view.mount(ListItem(Label(item)))

	def get_highlighted_index(self) -> int | None:
		olist = self.query_one("#orderable_list")
		if isinstance(olist, ListView):
			return olist.index
		return None

	def action_move_item_up(self):
		if self.get_highlighted_index() is not None and self.get_highlighted_index() > 0:
			self.list_items[self.get_highlighted_index()], self.list_items[self.get_highlighted_index() - 1] = (
				self.list_items[self.get_highlighted_index() - 1], self.list_items[self.get_highlighted_index()])
			self.redraw()

	def action_move_item_down(self):
		if self.get_highlighted_index() is not None and self.get_highlighted_index() < len(self.list_items) - 1:
			self.list_items[self.get_highlighted_index()], self.list_items[self.get_highlighted_index() + 1] = (
				self.list_items[self.get_highlighted_index() + 1], self.list_items[self.get_highlighted_index()])
			self.redraw()

	def action_delete_item(self):
		if self.get_highlighted_index() is not None:
			self.list_items.pop(self.get_highlighted_index())
			self.redraw()


class FileSelectionScreen(ModalScreen[str]):
	CSS_PATH = "css/file_selection.tcss"

	def __init__(self, path: str, select_files: bool = True):
		super().__init__()
		self.path = path
		self.selected_path = ""
		self.is_selecting_file = select_files

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "close_popup":
			self.dismiss("")
		elif event.button.id == "submit_popup":
			if self.selected_path != "":
				self.dismiss(self.selected_path)

	def compose(self) -> ComposeResult:
		yield Header()
		yield Footer()
		yield Vertical(
			Label("File Selection Screen", classes="h1"),
			VerticalScroll(
				DirectoryTree(path=self.path),
				id="file_list"),
			Horizontal(
				Button("Close", id="close_popup"),
				Button("Submit", id="submit_popup"),
				id="file_selection_buttons",
			),
			id="file_selection_dialog",
		)

	@on(DirectoryTree.DirectorySelected)
	def dir_selected(self, selected_dir: DirectoryTree.DirectorySelected):
		self.selected_path = selected_dir.path

	@on(DirectoryTree.FileSelected)
	def file_selected(self, selected_file: DirectoryTree.FileSelected):
		self.selected_path = selected_file.path


class PopupScreen(Screen[bool]):
	CSS_PATH = "css/popup.tcss"

	def __init__(self, popup_text: str, close_button_text: str):
		super().__init__()
		self.popup_text = popup_text
		self.close_button_text = close_button_text

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "close_popup":
			self.dismiss(False)


	def compose(self) -> ComposeResult:
		yield Vertical(
			Label(self.popup_text, classes="h1 prompt"),
			Button(self.close_button_text, id="close_popup"),
			classes="popup",
		)


class SelectMidiPortScreen(ModalScreen[str]):
	CSS_PATH = "css/select_midi_port.tcss"

	def __init__(self, midi_ports: list):
		super().__init__()
		self.midi_ports = midi_ports
		self.selected_port = ""

	def on_button_pressed(self, event: Button.Pressed) -> None:
		print(event.button.classes)
		if event.button.id == "close_popup":
			self.dismiss("")
		elif event.button.id == "submit_popup":
			if self.selected_port != "":
				self.dismiss(self.selected_port)
		elif event.button.id == "refresh_popup":
			self.midi_ports = mido.get_input_names()
			list_view = self.query_one("#midi_ports")
			if isinstance(list_view, VerticalScroll):
				list_view.remove_children()
				for index, port in enumerate(self.midi_ports):
					list_view.mount(Button(port, id=f"port_{index}"))
		elif "port_" in event.button.id:
			try:
				self.dismiss(mido.get_input_names()[int(event.button.id.replace("port_", ""))])
			except IndexError:
				self.app.push_screen(ErrorScreen(f"Specified port not found! Did you disconnect it?"))

	def compose(self) -> ComposeResult:
		yield Header()
		yield Footer()
		yield Vertical(
			Label("Select MIDI Port", classes="h1"),
			VerticalScroll(
				*[Button(port, id=f"port_{index}") for index, port in enumerate(mido.get_input_names())],
				id="midi_ports",
			),
			Horizontal(
				Button("Close", id="close_popup"),
				Button("Refresh", id="refresh_popup"),
				Button("Submit", id="submit_popup"),
				id="midi_port_buttons",
			),
			id="midi_port_dialog",
		)

	@on(ListView.Selected)
	def port_selected(self, selected: ListView.Selected):
		self.selected_port = self.midi_ports[self.query_one("#midi_ports").index]
		self.dismiss(self.selected_port)

	@on(ListView.Highlighted)
	def port_highlighted(self, highlighted: ListView.Highlighted):
		self.selected_port = self.midi_ports[self.query_one("#midi_ports").index]


class SettingsScreen(Screen):
	CSS_PATH = "css/settings.tcss"

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "back_to_menu":
			app.push_screen("main")
		elif event.button.id == "save_preferences":
			self.save_preferences()


	def compose(self) -> ComposeResult:
		yield Header()
		yield Footer()
		yield Vertical(
			Label("Settings Screen", classes="h1"),
			VerticalScroll(id="preferences"),
			Label("", id="settings_error", classes="error"),
			Horizontal(
				Button("Back to Menu", id="back_to_menu"),
				Button("Save", id="save_preferences"),
				id="settings_buttons",
			),
		)

	def _on_screen_resume(self) -> None:
		preference_box = self.query_one("#preferences")
		# delete all children
		for child in preference_box.children:
			child.remove()
		# add new children
		for preference in preferences.get_all_preferences():
			preference_name_label = Label(preference.preference_name, classes="preference_name")
			preference_name_label.tooltip = preference.description.replace("<br>", "\n")
			preference_box.mount(Horizontal(
				preference_name_label,
				Input(value=str(preference.value), id=preference.preference_name),
				classes="preference"
			))

	def save_preferences(self):
		preference_list = preferences.get_all_preferences()
		for preference in preference_list:
			this_input = self.query_one(f"#{preference.preference_name}")
			if this_input is not None and isinstance(this_input, Input):
				try:
					if isinstance(preference.value, bool):
						if is_recognized_boolean(this_input.value):
							preference.value = convert_string_to_boolean(this_input.value)
						else:
							self.query_one("#settings_error").update(f"Invalid value for preference: "
																	 f"{preference.preference_name} (expected boolean)")
							return
					elif isinstance(preference.value, int):
						preference.value = int(this_input.value)
					elif isinstance(preference.value, float):
						preference.value = float(this_input.value)
					elif isinstance(preference.value, str):
						preference.value = this_input.value
				except ValueError:
					self.query_one("#settings_error").update("Invalid value for preference: " + preference.preference_name)
					return
		preferences.set_preferences(preference_list)
		self.query_one("#settings_error").update("")


class ErrorScreen(ModalScreen):
	CSS_PATH = "css/error.tcss"

	def __init__(self, error_message: str):
		super().__init__()
		self.error_message = error_message

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "close_popup":
			self.dismiss(False)

	def compose(self) -> ComposeResult:
		yield Vertical(
			Label("ERROR", classes="h1 error error_label"),
			Label(self.error_message, classes="h1 error_label"),
			Button("Close", id="close_popup"),
			classes="popup",
	)


class PerformanceScreen(Screen):
	BINDINGS = [
		("space", "next_patch", "Next Patch"),
		("backspace", "previous_patch", "Previous Patch"),
		("l", "next_patch_file", "Next File"),
		("a", "previous_patch_file", "Previous File"),
	]

	CSS_PATH = "css/performance_screen.tcss"

	def __init__(self, files: list, midi_port: str):
		super().__init__()
		self.files = files
		self.midi_port = midi_port
		self.current_file_index = 0
		self.current_patch_index = 0
		self.process = None
		self.pedal_event = multiprocessing.Event()
		self.pedal_queue = multiprocessing.Queue()

	def compose(self) -> ComposeResult:
		yield Header()
		yield Footer()
		yield Horizontal(
			Vertical(
				Label("Current Patch: 0 Testtest", classes="h1", id="current_patch"),
				VerticalScroll(
					id="patch_list",
				),
			),
			Vertical(
				Vertical(
					id="patch_comments"
				),
				Vertical(
					id="patch_info"
				),
				id="info_container",
			),
			id="performance_screen",
		)

	def on_button_pressed(self, event: Button.Pressed):
		button_class = event.button.classes
		for i in button_class:
			if "patch_button_" in i:
				button_id = int(i.replace("patch_button_", ""))
				self.current_patch_index = button_id
				self.update()
				return

	def on_mount(self) -> None:
		self.update()
		self.set_interval(0.1, self.check_pedal_queue)

	def update(self):
		current_file = self.files[self.current_file_index]
		this_patch_list = patcher.get_patch_list(current_file)
		this_patch_file = patcher.parse_patch_from_file(current_file)
		this_int_patch_list = patcher.get_int_list(this_patch_file)
		this_comment_list = patcher.get_comment_list(this_patch_file)
		this_patch_name = this_patch_file["patch_name"]

		next_file_path = self.files[self.current_file_index + 1] if self.current_file_index + 1 < len(
			self.files) else self.files[0]
		next_patch_name = patcher.parse_patch_from_file(next_file_path)["patch_name"]

		try:
			with mido.open_output(self.midi_port) as outport:
				outport.send(mido.Message("program_change", program=this_int_patch_list[self.current_patch_index]))
		except Exception as e:
			self.app.push_screen(ErrorScreen(str(e)))

		patch_list = self.query_one("#patch_list")

		for i in patch_list.children:
			i.remove()

		patch_list.remove_children()
		if isinstance(patch_list, VerticalScroll):
			for index, patch in enumerate(this_patch_list):
				classes = "selected_patch" if index == self.current_patch_index else ""
				new_button = Button(str(patch["sound"]), classes=classes + f" patch_button_{index}")
				patch_list.mount(new_button)
				if classes == "selected_patch":
					new_button.scroll_visible()

		comments = self.query_one("#patch_comments")
		comments.remove_children()
		if isinstance(comments, Vertical):
			comments.mount(Label(f"Comments\n\n{this_comment_list[self.current_patch_index]}"))

		patch_name = self.query_one("#current_patch")
		if isinstance(patch_name, Label):
			patch_name.update(f"Current Patch: {this_patch_name}")


		def on_pedal_event():
			self.action_next_patch()

		if self.process is not None:
			self.process.kill()
			self.process.join()

		self.pedal_event.clear()
		self.process = multiprocessing.Process(target=self.wait_for_switch_pedal, args=(self.midi_port, self.pedal_event, self.pedal_queue))
		self.process.start()

	def action_next_patch(self):
		self.current_patch_index += 1
		if self.current_patch_index >= len(patcher.get_patch_list(self.files[self.current_file_index])):
			self.current_patch_index = 0
			self.current_file_index += 1
			if self.current_file_index >= len(self.files):
				self.current_file_index = 0
		self.update()

	def action_previous_patch(self):
		self.current_patch_index -= 1
		if self.current_patch_index < 0:
			self.current_file_index -= 1
			if self.current_file_index < 0:
				self.current_file_index = len(self.files) - 1

			current_file = self.files[self.current_file_index]
			this_patch_list = patcher.get_patch_list(current_file)
			self.current_file_index = len(this_patch_list) - 1
		self.update()

	def action_next_patch_file(self) -> None:
		self.current_file_index += 1
		if self.current_file_index >= len(self.files):
			self.current_file_index = 0
		self.current_patch_index = 0
		self.update()

	def action_previous_patch_file(self) -> None:
		self.current_file_index -= 1
		if self.current_file_index < 0:
			self.current_file_index = len(self.files) - 1
		self.current_patch_index = 0
		self.update()

	def wait_for_switch_pedal(self, port: str, event, queue: multiprocessing.Queue):
		with (mido.open_input(port) as inport):
			for msg in inport:
				print("Message!")
				if event.is_set():
					return
				if msg.type == "control_change" and msg.control == 82 and msg.value > int(preferences.get_preference_value("switch_pedal_sensitivity")):
					queue.put("pedal_down")
					return

	def check_pedal_queue(self):
		try:
			message = self.pedal_queue.get_nowait()
			if message == "pedal_down":
				self.action_next_patch()
		except Exception as e:
			pass



class PerformanceSetupScreen(Screen):
	CSS_PATH = "css/performance.tcss"

	orderable_list: OrderableListWidget = None

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "back_to_menu":
			app.push_screen("main")
		elif event.button.id == "add_file":
			self.app.push_screen(FileSelectionScreen(file_manager.get_patch_directory(), select_files=True),
								 self.selected_file)
		elif event.button.id == "add_folder":
			self.app.push_screen(FileSelectionScreen(file_manager.get_patch_directory(), select_files=False),
								 self.selected_folder)
		elif event.button.id == "sort_items":
			self.orderable_list.list_items = sort_list_by_numbering_system(self.orderable_list.list_items, False)
			self.orderable_list.redraw()
		elif event.button.id == "start_performance":
			if len(self.orderable_list.list_items) == 0:
				self.app.push_screen(ErrorScreen("No patches selected. Please select some patches to perform."))
				return
			self.app.push_screen(SelectMidiPortScreen(mido.get_input_names()), self.selected_midi_port)


	def selected_midi_port(self, port: str):
		if port == "": return
		self.app.push_screen(PerformanceScreen(
			[file_manager.get_patch_directory_from_patch(i) for i in self.orderable_list.list_items], port))


	def selected_file(self, path: str):
		if path == "": return
		self.orderable_list.list_items.append(file_manager.remove_patch_directory_from_patch(str(path)))
		self.orderable_list.redraw()

	def selected_folder(self, path: str):
		if path == "": return
		files: list = [file_manager.remove_patch_directory_from_patch(str(path) + "/" + i) for i in file_manager.get_files_in_dir(path)]
		for file in files:
			self.orderable_list.list_items.append(str(file))
		self.orderable_list.redraw()


	def compose(self) -> ComposeResult:
		yield Header()
		yield Footer()
		self.orderable_list = OrderableListWidget([])
		yield Vertical(
			Label("Performance Screen", classes="h1"),
			Horizontal (
				Button("Add File", id="add_file"),
				Button("Add Folder", id="add_folder"),
			),
			self.orderable_list,
			Horizontal (
				Button("Sort Items", id="sort_items"),
				Button("Back to Menu", id="back_to_menu"),
				Button("Start Performance", id="start_performance"),
			),
		)


class MainScreen(Screen):
	CSS_PATH = "css/main.tcss"
	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "settings":
			app.push_screen("settings")
		elif event.button.id == "performance":
			app.push_screen("performance")


	def compose(self) -> ComposeResult:
		yield Header()
		yield Footer()
		Label("Main Screen", classes="h1"),
		yield Vertical(
			Label("Main Screen", classes="h1"),
			Button("Button 1", id="midi_device"),
			Button("Performance", id="performance"),
			Button("Settings", id="settings"),
		)


class MainApp(App):
	TITLE = "Midi Controller"

	BINDINGS = {
	}

	def create_popup(self, popup_text: str, close_button_text: str) -> None:
		def on_popup_dismissed(result: bool) -> None:
			self.pop_screen()

		self.push_screen(PopupScreen(popup_text, close_button_text))

	def on_mount(self) -> None:
		self.install_screen(SettingsScreen(), name="settings")
		self.install_screen(PerformanceSetupScreen(), name="performance")
		self.install_screen(MainScreen(), name="main")
		self.push_screen("main")


if __name__ == "__main__":
	create_needed_files()
	app = MainApp()
	app.run()