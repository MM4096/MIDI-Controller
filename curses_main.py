import curses
import json
import multiprocessing
import os
from os.path import join as path_join
import re
import time
from curses import wrapper
from curses.textpad import Textbox
import mido
import mido.backends.rtmidi

from modules import file_manager, preferences, tools, patcher
from modules.command import run_command, Command
from modules.tools import sort_list_by_numbering_system

# region colors


curses.initscr()
curses.start_color()
curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

RED_TEXT = curses.color_pair(1)
GREEN_TEXT = curses.color_pair(2)
YELLOW_TEXT = curses.color_pair(3)

# endregion

# region inputs

KEY_UP = [65, 259]
KEY_DOWN = [66, 258]
KEY_LEFT = [68, 260]
KEY_RIGHT = [67, 261]
KEY_ENTER = [10, 13]
KEY_BACKSPACE = [127, 263]
KEY_SPACE = [32]
KEY_ESCAPE = [27]
KEY_SLASH = [47]
KEY_NUMBERS = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
KEY_LETTERS = [65, 122]

# endregion

pedal_pressed = False


def print_and_wait(stdscr: curses.window, text: str, wait_for_enter: bool = True):
	stdscr.addstr(text)
	stdscr.refresh()
	if wait_for_enter:
		stdscr.getch()


def create_needed_files():
	file_manager.create_dir_if_not_exists(file_manager.get_user_data_dir())
	file_manager.create_dir_if_not_exists(path_join(file_manager.get_user_data_dir(), "patches"))
	file_manager.create_dir_if_not_exists(path_join(file_manager.get_user_data_dir(), "presets"))
	file_manager.create_dir_if_not_exists(path_join(file_manager.get_user_data_dir(),  "temp"))
	new_preferences = preferences.update_preferences()


def wait_for_switch_pedal(port: str, event):
	global pedal_pressed
	with (mido.open_input(port) as inport):
		for msg in inport:
			if msg.type == "control_change" and msg.control == 82 and msg.value > int(preferences.get_preference_value("switch_pedal_sensitivity")):
				event.set()
				return


def get_main_port():
	with open(file_manager.get_file_path("main_port.data"), "r") as f:
		return f.read()


def is_port_connected(_port: str) -> bool:
	return get_ports().count(_port) > 0


def fix_screen_size(stdscr: curses.window):
	while True:
		target_width = 100
		target_height = 30
		height, width = stdscr.getmaxyx()

		stdscr.erase()
		if height >= target_height and width >= target_width:
			return
		else:
			stdscr.addstr(f"Window is too small! Please resize to a minimum [height]:[width] of "
						  f"{target_height}:{target_width}!(is {height}:{width})")

		stdscr.refresh()


def set_main_port(_port: str):
	if preferences.get_preference_value("save_midi_port"):
		if "Midi Through" in _port:
			pass
		else:
			with open(file_manager.get_file_path("main_port.data"), "w") as f:
				f.write(_port)


def get_ports() -> list:
	return mido.get_input_names()


def port_options() -> str:
	ports = get_ports()

	# see if saved port is available
	main_port = get_main_port()
	if main_port in ports:
		return main_port
	index, port = select_options(ports, "Select a port to connect to", ">", 0)
	set_main_port(port)
	return port


def create_input(max_length: int = 20, title: str = "Input") -> str:
	back_window = curses.newwin(50, 100, 0, 0)
	back_window.erase()
	back_window.refresh()

	new_window = curses.newwin(len(title.split("\n")) + 3, max(max_length, len(title) + 2), 0, 0)
	new_window.erase()
	new_window.addstr(title + "\n")
	new_window.refresh()
	if preferences.get_preference_value("use_emacs_text_editor_for_inputs"):
		# create input box
		win = curses.newwin(1, max_length, len(title.split("\n")) + 1, 0)
		box = Textbox(win)
		new_window.refresh()
		box.edit()
		return box.gather()
	else:
		# set cursor position to be inside box
		new_window.move(len(title.split("\n")), 0)
		new_window.refresh()
		# create input box
		input_string = ""
		while True:
			this_input = new_window.getch()
			if this_input in KEY_BACKSPACE:
				input_string = input_string[:-1]
			elif this_input in KEY_ENTER:
				break
			elif len(input_string) + 1 < max_length:
				input_string += chr(this_input)
			new_window.erase()
			new_window.addstr(title + "\n")
			new_window.addstr(input_string)
			new_window.refresh()
		return input_string


def select_options(options: list[str], title: str, indicator: str = ">", default_index: int = 0) -> (int, str):
	set_cursor_visibility(False)
	index = tools.clampi(default_index, 0, len(options) - 1)
	not_selected_string = ""
	for i in range(len(indicator)):
		not_selected_string += " "
	new_window = curses.newwin(50, 100, 0, 0)
	while True:
		new_window.erase()
		new_window.addstr(title + "\n")

		cut_options, start_index = tools.cut_array(options, index, 15)
		has_options_before: bool = start_index > 0
		has_options_after: bool = tools.is_sublist_with_more_elements(options, cut_options, start_index)
		new_window.addstr("/\\\n" if has_options_before else "")
		for i in range(len(cut_options)):
			new_window.addstr(f"{not_selected_string if index != i + start_index else indicator} {cut_options[i]}\n")
		if has_options_after:
			new_window.addstr("\\/")
		new_window.refresh()
		this_input = new_window.getch()
		if this_input in KEY_UP:
			index = tools.clampi(index - 1, 0, len(options) - 1)
		elif this_input in KEY_DOWN:
			index = tools.clampi(index + 1, 0, len(options) - 1)
		elif this_input in KEY_ENTER:
			break
	set_cursor_visibility(True)
	return index, options[index]


def select_options_multiple(options: list[str], title: str, indicator: str = ">", selected: str = "*") -> (
		int, list[str]):
	set_cursor_visibility(False)
	selected_options: list[bool] = []
	for i in options:
		selected_options.append(False)
	not_selected_string = ""
	for i in range(len(selected)):
		not_selected_string += " "
	not_indicated_string = ""
	for i in range(len(indicator)):
		not_indicated_string += " "
	new_window = curses.newwin(50, 100, 0, 0)
	index = 0
	options.append("Select")
	while True:
		new_window.erase()
		new_window.addstr(title + "\n")

		cut_options, start_index = tools.cut_array(options, index, 15)
		has_options_before: bool = start_index > 0
		has_options_after: bool = tools.is_sublist_with_more_elements(options, cut_options, start_index)
		new_window.addstr("/\\\n" if has_options_before else "\n")
		for i in range(len(cut_options)):
			new_window.addstr(f"{indicator if i + start_index == index else not_indicated_string} "
							  f"{selected if i + start_index < len(options) - 1 and selected_options[i + start_index] else not_selected_string} "
							  f"{options[i + start_index]}\n")
		if has_options_after:
			new_window.addstr("\\/")

		new_window.refresh()
		this_input = new_window.getch()
		if this_input in KEY_UP:
			index = tools.clampi(index - 1, 0, len(options) - 1)
		elif this_input in KEY_DOWN:
			index = tools.clampi(index + 1, 0, len(options) - 1)
		elif this_input in KEY_ENTER:
			if index == len(options) - 1:
				# pressed select
				break
			else:
				selected_options[index] = not selected_options[index]
	set_cursor_visibility(True)
	return index, [options[i] for i in range(len(options) - 1) if selected_options[i]]


def scroll_view(stdscr: curses.window, items: list[str], text_before: str = "", text_after: str = ""):
	index = tools.clampi(7, 0, len(items) - 1)
	while True:
		stdscr.erase()
		cut_options, start_index = tools.cut_array(items, index, 15)
		has_options_before: bool = start_index > 0
		has_options_after: bool = tools.is_sublist_with_more_elements(items, cut_options, start_index)
		stdscr.addstr(text_before + "\n")
		stdscr.addstr("/\\\n" if has_options_before else "\n")
		for i in range(len(cut_options)):
			stdscr.addstr(f" {cut_options[i]}\n")
		if has_options_after:
			stdscr.addstr("\\/")
		stdscr.addstr("\n" + text_after)
		stdscr.refresh()
		this_input = stdscr.getch()
		if this_input in KEY_UP:
			index = tools.clampi(index - 1, 7, len(items) - 8)
		elif this_input in KEY_DOWN:
			index = tools.clampi(index + 1, 7, len(items) - 8)
		elif this_input in KEY_ENTER:
			break


def set_up_preferences(stdscr, new_preferences: list[preferences.Preference]):
	return
	# TODO: Functionality
	added_all_preferences = len(new_preferences) == len(preferences.initial_preferences)
	if added_all_preferences:
		stdscr.addstr("Welcome to preference setup! Here, you'll set up all the config stuff. "
					  "All this can be changed later. (Any key to continue)")
		stdscr.refresh()
		stdscr.getch()
	else:
		index, option = select_options(["Yes", "No"],
									   "Some new preferences have been added. Would you like to change them?")
		if index == 1:
			return
	stdscr.erase()
	for preference in new_preferences:
		input_text = (f"{preference.preference_name}\n"
					  f"{preference.description}\n"
					  f"[y]/[n]")

		stdscr.clear()
		stdscr.addstr(input_text)
		stdscr.refresh()
		stdscr.getch()
		value = create_input(100, input_text)
		if value.lower == "y":
			preferences.set_preference(preference.preference_name, True)
		else:
			preferences.set_preference(preference.preference_name, False)


def set_cursor_visibility(visibility: bool):
	curses.curs_set(1 if visibility else 0)


def open_program_data(stdscr: curses.window):
	while True:
		options = ["Open patches folder", "Open presets folder", "Open preferences file", "Back"]
		index, option = select_options(options, "Open program data", ">", 0)
		if index == 0:
			run_command(Command.OPEN_DIRECTORY, f"{file_manager.get_patch_directory()}")
		elif index == 1:
			run_command(Command.OPEN_DIRECTORY, f"{file_manager.get_config_directory()}/")
		elif index == 2:
			run_command(Command.WRITE_FILE, f"{file_manager.get_file_path("preferences")}")
		elif index == 3:
			break
		stdscr.erase()
		stdscr.refresh()


def select_file(default_path: str, title: str = "Select a file!", allow_leaving_default_path: bool = False,
				filter_extension: str = ""):
	while True:
		split_path = default_path.split("/")
		directories = file_manager.get_dirs_in_dir(default_path)
		files = [i for i in file_manager.get_files_in_dir(default_path) if i.endswith(filter_extension)]
		files = sort_list_by_numbering_system(files)

		directory_display = ["/" + i for i in directories]
		options = [".."] + directory_display + files + ["Back"]
		index, option = select_options(options, title + f"\n{default_path}", ">", 0)
		if index == 0:
			split_path.pop(-1)
			if os.path.samefile("/".join(split_path), default_path):
				if not allow_leaving_default_path:
					continue
			if os.path.samefile("/".join(split_path), file_manager.get_user_data_dir()):
				continue
			default_path = "/".join(split_path)
		else:
			index -= 1
			if index < len(directories):
				default_path += "/" + directories[index]
			elif index < len(directories) + len(files):
				return default_path + "/" + files[index - len(directories)]
			else:
				return ""


def select_directory(default_path: str, title: str = "Select a directory!", allow_leaving_default_path: bool = False):
	while True:
		split_path = default_path.split("/")
		directories = file_manager.get_dirs_in_dir(default_path)
		directory_display = ["/" + i for i in directories]
		options = [".."] + directory_display + ["Select Folder", "New Folder", "Back"]
		index, option = select_options(options, title + f"\n{default_path}", ">", 0)
		if index == 0:
			split_path.pop(-1)
			if os.path.samefile("/".join(split_path), default_path):
				if not allow_leaving_default_path:
					continue
			if os.path.samefile("/".join(split_path), file_manager.get_user_data_dir()):
				continue
			default_path = "/".join(split_path)
		else:
			index -= 1
			if index < len(directories):
				default_path += "/" + directories[index]
			else:
				index -= len(directories)
				if index == 0:
					return default_path
				elif index == 1:
					new_folder_name = create_input(50, "Enter the name of the new folder")
					file_manager.create_dir_if_not_exists(f"{default_path}/{new_folder_name}")
					default_path = f"{default_path}/{new_folder_name}"
				else:
					return ""


def edit_config(previous_config: dict, allow_adding_preset: bool = False) -> dict:
	saved_config = previous_config.copy()
	new_window = curses.newwin(50, 50, 0, 0)
	new_window.erase()
	while True:
		current_keys = list(previous_config.keys())
		options = ["\t" + i for i in current_keys.copy()]
		options += ["Add new key", "Remove key", "Save and exit", "Exit without saving"]
		if allow_adding_preset:
			options += ["Add preset"]
		index, option = select_options(options, "Edit config\nSelect a key to edit", ">", 0)
		new_window.erase()
		new_window.refresh()
		if index < len(current_keys):
			# edit key
			selected_key = current_keys[index]
			index, option = select_options(["Edit key", "Edit value", "Back"],
										   f"Editing key [{selected_key}]", ">", 0)
			if index == 0:
				new_key = create_input(20, f"Enter the new name of the key (was [{selected_key}])")
				previous_config[new_key] = previous_config[selected_key]
				del previous_config[selected_key]
			elif index == 1:
				new_value = create_input(20, f"Enter the new value of the key [{selected_key}] "
											 f"(was [{previous_config[selected_key]}])")
				previous_config[selected_key] = new_value
		else:
			if index == len(current_keys):
				# add new key
				stop = False
				while not stop:
					name = create_input(20, "Enter the name of the new key")
					if name in current_keys:
						index, option = select_options(["Yes", "No"],
													   "That key already exists. Would you like to overwrite it?",
													   ">", 1)
						if index == 1:
							continue
					value = create_input(20, "Enter the value of the new key")
					previous_config[name] = value
					stop = True
			elif index == len(current_keys) + 1:
				# remove key
				remove_options = current_keys.copy()
				remove_options += ["Cancel"]
				index, option = select_options(remove_options, "Select a key to remove", ">", 0)
				if index < len(current_keys):
					index, option2 = select_options(["Yes", "No"],
													f"Are you sure you want to remove the key [{option}]?",
													">", 0)
					if index == 0:
						del previous_config[option]
				else:
					pass
			elif index == len(current_keys) + 2:
				# save and exit
				return previous_config
				pass
			elif index == len(current_keys) + 3:
				# exit without saving
				index, option = select_options(["Yes", "No"], "Are you sure you want to exit without saving?", ">", 1)
				if index == 0:
					return saved_config
				else:
					pass
			elif index == len(current_keys) + 4:
				# add preset
				preset_name = create_input(20, "Enter the name of the preset")
				previous_config["preset"] = preset_name


def edit_absolute_config(stdscr: curses.window):
	stdscr.erase()
	index, option = select_options(["Create new config", "Edit existing config"], "Config editing", ">", 0)
	if index == 0:
		folder_path = select_directory(file_manager.get_config_directory(),
									   "Select a folder to create the config in", False)
		if folder_path == "":
			edit_absolute_config(stdscr)
		else:
			name = create_input(50, "Enter the name of the new config")
			new_config = edit_config({}, False)
			file_manager.write_data(json.dumps(new_config), f"{folder_path}/{name}.midiconfig")
	else:
		config_path = select_file(file_manager.get_config_directory(), "Select a config file", True,
								  ".midiconfig")
		if config_path == "":
			return
		config = patcher.parse_preset(config_path)
		new_config = edit_config(config, False)
		patcher.write_data(json.dumps(new_config), config_path)


def edit_patch(stdscr: curses.window):
	stdscr.erase()
	stdscr.refresh()
	patch_path = ""
	index, option = select_options(["Create new patch", "Edit existing patch"], "Patch editing", ">", 0)
	if index == 0:
		folder_path = select_directory(file_manager.get_patch_directory(),
									   "Select a folder to create the patch in", False)
		if folder_path == "":
			edit_patch(stdscr)
		else:
			stdscr.erase()
			stdscr.refresh()
			name = create_input(50, "Enter the name of the new patch")
			patcher.write_data(patcher.compile_patch({}, [], ""), f"{folder_path}/{name}.midipatch")
			patch_path = f"{folder_path}/{name}.midipatch"
	elif index == 1:
		patch_path = select_file(file_manager.get_patch_directory(), "Select a patch file", True,
								 ".midipatch")
		if patch_path == "":
			edit_patch(stdscr)
	else:
		return

	patch = patcher.parse_patch_from_file(patch_path)
	patch_name = patch["patch_name"]
	patch_config = patch["patch_config"]
	patch_list = patch["patch_list"]["list"]

	value = preferences.get_preference_value("default_preset")
	if isinstance(value, str) and value != "" and "preset" not in patch_config:
		index, option = select_options(["Yes", "No"], f"Would you like to use the default preset [{value}]?", ">", 0)
		if index == 0:
			patch_config["preset"] = value
			patcher.write_data(patcher.compile_patch(patch_config, patch_list, patch_name), patch_path)

	while True:
		index, option = select_options(["Edit patch config", "Edit patch list (gedit)", "Back"],
									   "Editing patch", ">", 0)
		if index == 0:
			new_config = edit_config(patch_config, True)
			patcher.write_data(patcher.compile_patch(new_config, patch_list, patch_name), patch_path)
		elif index == 1:
			available_presets = patcher.get_available_presets(patch_path)
			available_presets.pop(0)
			available_presets[0] = "\n\t# " + available_presets[0]
			file_data = ("# edit patches here. Either [string] (referring to a patch config) or [int] "
						 "(referring to that item) is allowed\n"
						 "# comments start with [#] \n\n"
						 "# Enter the patch name on the next line\n\n"
						 f"{patch_path.split("/")[-1]}\n\n"
						 f"\t# Here's the usable presets. To add more, edit the [CONFIG] section.\n"
						 f"{'\n\t# '.join(available_presets)}\n\n"
						 "# Leave the next line the way it currently is\n"
						 "startlist\n"
						 "# start patching here\n"
						 "# use '--' after a sound to declare a comment (having no '--' will result in no comment)\n")
			file_data += "\n".join([f"{i['sound']} -- {i['comments']}" for i in patch_list])
			with open(file_manager.get_file_path("temp/patch_list.temp"), "w") as f:
				f.write(file_data)
			run_command(Command.WRITE_FILE, file_manager.get_file_path("temp/patch_list.temp"))
			stdscr.clear()
			stdscr.refresh()
			with open(file_manager.get_file_path("temp/patch_list.temp"), "r") as f:
				given_list = f.read().splitlines()
			os.remove(file_manager.get_file_path("temp/patch_list.temp"))
			list_copy: list = []
			for line in given_list:
				removed_spaces = line.replace(" ", "").replace("\t", "")
				if removed_spaces == "":
					pass
				elif removed_spaces[0] == "#":
					pass
				else:
					list_copy.append(line)
			patch_list = []
			found_start = False
			for line in list_copy:
				if line == "startlist":
					found_start = True
				elif found_start:
					line_split: list = line.split("--")
					if len(line_split) == 1:
						line_split.append("")
					patch_list.append({"sound": line_split[0].strip(), "comments": line_split[1].strip()})
				elif line != "":
					patch_name = line
			patcher.write_data(patcher.compile_patch(patch_config, patch_list, patch_name), patch_path)
		elif index == 2:
			return


def patch_editing_page(stdscr: curses.window):
	while True:
		options = ["Create/Edit patches", "Create/Edit configs", "Back"]
		index, option = select_options(options, "Patch editing", ">", 0)
		stdscr.erase()
		if index == 0:
			edit_patch(stdscr)
		elif index == 1:
			edit_absolute_config(stdscr)
		elif index == 2:
			break

def preferences_page(stdscr: curses.window):
	while True:
		options = ["Edit with external program", "Back"]
		index, option = select_options(options, "Editing Preferences", ">", 0)
		stdscr.erase()
		if index == 0:
			run_command(Command.WRITE_FILE, file_manager.get_file_path("preferences"))
			stdscr.clear()
			stdscr.refresh()
		elif index == 1:
			break


def performance_mode(stdscr: curses.window):
	performance_files = []
	display_files = []
	stdscr.erase()
	stdscr.refresh()
	if not preferences.get_preference_value("skip_performance_mode_info"):
		stdscr.addstr("Welcome to Performance Mode! [Any key to continue]")
		stdscr.refresh()
		stdscr.getch()
		stdscr.erase()
		stdscr.addstr("To exit Performance Mode, press [q].\n")
		stdscr.addstr("To switch to the next patch, press [Enter] or [SPACE].\n")
		stdscr.addstr("To switch to the previous patch, press [Backspace] or [UP_ARROW].\n")
		stdscr.addstr("[Any key to continue]\n")
		stdscr.refresh()
		stdscr.getch()
		stdscr.erase()
		stdscr.refresh()
	available_ports = get_ports()
	preferred_port = get_main_port()
	if preferred_port not in available_ports:
		preferred_port = port_options()
	selected_files = False
	while not selected_files:
		stdscr.erase()
		stdscr.refresh()
		index, option = select_options(["Perform a single patch", "Perform a list of patches from a folder",
										"Perform a list of patches in a folder (select from folder)", "Back"],
									   "Performance Mode", ">", 0)
		if index == 0:
			patch_path = select_file(file_manager.get_patch_directory(), "Select a patch file", True,
									 ".midipatch")
			if patch_path == "":
				continue
			performance_files = sort_list_by_numbering_system([patch_path])
			display_files = sort_list_by_numbering_system([patch_path], True)
			selected_files = True
		elif index == 1:
			folder_path = select_directory(file_manager.get_patch_directory(), "Select a folder", False)
			if folder_path == "":
				continue
			performance_files = [folder_path + "/" + i for i in file_manager.get_files_in_dir(folder_path) if
								 i.endswith(".midipatch")]
			performance_files = sort_list_by_numbering_system(performance_files)
			display_files = sort_list_by_numbering_system(performance_files, True)
			selected_files = True
		elif index == 2:
			folder_path = select_directory(file_manager.get_patch_directory(), "Select a folder", False)
			if folder_path == "":
				continue
			performance_files = select_options_multiple(
				sort_list_by_numbering_system([i for i in file_manager.get_files_in_dir(folder_path) if
											   i.endswith("midipatch")]), "Select patches to perform")[1]
			performance_files = [f"{folder_path}/{i}" for i in performance_files]
			performance_files = sort_list_by_numbering_system(performance_files)
			selected_files = True
			display_files = sort_list_by_numbering_system(performance_files, True)
		else:
			return
		list_of_files = [i.split("/")[-1].replace(".midipatch", "") for i in display_files]
		stdscr.erase()
		stdscr.refresh()
		# index, option = select_options(["Yes", "No"], "Here's a list of files to perform. Is this OK?"
		#                                               "\n" + "\n".join(list_of_files), ">", 0)
		scroll_view(stdscr, list_of_files, "Files to perform:", "Press [Enter] to continue")
		break

	index = 0
	if len(list_of_files) > 1:
		index, option = select_options([i.split("/")[-1].replace(".midipatch", "") for i in display_files],
									   "Which patch would you like to start with?", ">", 0)

	stdscr.erase()
	stdscr.refresh()

	while True:
		try:
			outport = mido.open_output(preferred_port)
			break
		except OSError:
			stdscr.erase()
			stdscr.addstr(f"Connection [{preferred_port}] not connected! Waiting for a connection...")
	current_file_index = index
	current_patch_index = 0
	cached_index = -1
	cached_file_index = -1
	stop = False
	skip_input_wait = False
	first_run_through = True
	while not stop:
		set_cursor_visibility(False)
		skip_input_wait = False

		current_file_path = performance_files[current_file_index]
		this_patch_list = patcher.parse_patch_from_file(current_file_path)
		this_int_patch_list = patcher.get_int_list(this_patch_list)
		this_comment_list = patcher.get_comment_list(this_patch_list)
		next_file_path = performance_files[current_file_index + 1] if current_file_index + 1 < len(
			performance_files) else performance_files[0]
		next_patch_name = patcher.parse_patch_from_file(next_file_path)["patch_name"]
		all_patch_names_list = [patcher.parse_patch_from_file(i)["patch_name"] for i in performance_files]

		if first_run_through:
			first_run_through = False
			# put functions to run only on the first time here...

		if cached_index != current_patch_index or cached_file_index != current_file_index:
			cached_index = current_patch_index
			cached_file_index = current_file_index
			clamped_index = tools.clampi(current_patch_index, 0, len(this_int_patch_list) - 1)

			while True:
				try:
					outport.send(mido.Message("program_change", program=this_int_patch_list[clamped_index]))
					break
				except OSError:
					stdscr.erase()
					stdscr.addstr(f"Connection [{preferred_port}] not connected! Waiting for a connection...")

			# region display info
			stdscr.erase()
			current_file_name = patcher.parse_patch_from_file(current_file_path)["patch_name"]
			stdscr.addstr(f"Current patch: {current_file_name}\n")

			patch_list = patcher.get_patch_list(current_file_path)
			cut_list, starting_index = tools.cut_array(patch_list, current_patch_index, 15)
			has_items_before: bool = starting_index > 0
			has_items_after: bool = tools.is_sublist_with_more_elements(patch_list, cut_list, starting_index)
			stdscr.addstr("/\\\n" if has_items_before else "\n")
			for i in range(len(cut_list)):
				modifier = ">" if current_patch_index == i + starting_index else " "
				stdscr.addstr(f" {modifier}  {cut_list[i]["sound"]}\n")
			if has_items_after:
				stdscr.addstr("\\/\n")
			if current_patch_index >= len(this_int_patch_list):
				if not preferences.get_preference_value("only_require_one_press_for_next_patch"):
					pass
				else:
					current_patch_index += 1
					skip_input_wait = True
				stdscr.addstr(" >  [END OF PATCH LIST]")
			else:
				stdscr.addstr("    [END OF PATCH LIST]")
			stdscr.addstr(f"\n\nNext patch: {next_patch_name}\n")
			stdscr.addstr("\n\n\n")
			stdscr.addstr(f"Notes:\n\n\n{this_comment_list[clamped_index]}\n")
			stdscr.refresh()
			# endregion

		direction = 0
		global pedal_pressed
		list_of_files = []
		pedal_pressed = False
		pedal_event = multiprocessing.Event()
		process = multiprocessing.Process(target=wait_for_switch_pedal, args=[preferred_port, pedal_event])
		process.start()
		stdscr.nodelay(True)
		stdscr.timeout(100)

		arrow_direction: int = 0
		while not pedal_event.is_set() and not skip_input_wait:
			this_input = stdscr.getch()
			if this_input in KEY_ENTER or this_input in KEY_SPACE or this_input in KEY_DOWN:
				direction = 1
				break
			elif this_input in KEY_BACKSPACE or this_input in KEY_UP:
				direction = -1
				break
			elif this_input in KEY_ESCAPE:
				stop = True
				break

			if this_input in KEY_LEFT:
				if arrow_direction == -1:
					current_file_index = tools.clampi(current_file_index - 1, 0, len(performance_files) - 1)
					current_patch_index = -1
					break
				arrow_direction = -1
			elif this_input in KEY_RIGHT:
				if arrow_direction == 1:
					current_file_index = tools.clampi(current_file_index + 1, 0, len(performance_files) - 1)
					current_patch_index = -1
					break
				arrow_direction = 1

			if this_input in KEY_SLASH:
				current_command: str = "/"
				new_window = curses.newwin(2, 100, 0, 0)

				_stop = False
				while not _stop:
					this_input = stdscr.getch()

					if this_input in KEY_NUMBERS or (KEY_LETTERS[0] <= this_input <= KEY_LETTERS[1]):
						current_command += chr(this_input)
					elif this_input in KEY_SPACE:
						current_command += " "
					elif this_input in KEY_BACKSPACE:
						current_command = current_command[:-1]
						if len(current_command) == 0:
							current_command = "/"
					elif this_input in KEY_ESCAPE:
						_stop = True
					elif this_input in KEY_ENTER:
						current_command = current_command[1:]
						split = current_command.split(" ")
						if split[0] == "goto" and len(split) > 1:
							joined_query = " ".join(split[1:])
							for i in all_patch_names_list:
								if i.lower().startswith(joined_query.lower()):
									cached_file_index = -1
									current_file_index = all_patch_names_list.index(i)
									break
							for i in all_patch_names_list:
								if joined_query.lower() in i.lower():
									cached_file_index = -1
									current_file_index = all_patch_names_list.index(i)
									break
							stdscr.addstr(0, 0, "[goto]: Match not found.")
						elif split[0] == "exit":
							return
						elif split[0] == "next":
							current_file_index += 1
						elif split[0] == "prev":
							current_file_index -= 1

						_stop = True


					split_command = current_command[1:]
					split = split_command.split(" ")
					command_text: str = "Entering a command..."

					if split[0] == "goto":
						command_text = "[goto]: Go to the first file that matches the input"
					elif split[0] == "exit":
						command_text = "[exit]: Exit performance mode"
					elif split[0] == "next":
						command_text = "[next]: Go to the next file in the list"
					elif split[0] == "prev":
						command_text = "[prev]: Go to the previous file in the list"

					new_window.erase()
					new_window.addstr(f"{command_text}\n")
					new_window.addstr(current_command)
					new_window.refresh()
				new_window.clear()
				new_window.refresh()
				break


		if pedal_event.is_set():
			direction = 1

		process.kill()
		process.join()
		current_patch_index += direction
		if current_patch_index < 0:
			if preferences.get_preference_value("allow_backtracking_in_performance_mode"):
				current_file_index -= 1
			current_file_path = performance_files[current_file_index]
			this_patch_list = patcher.parse_patch_from_file(current_file_path)
			this_int_patch_list = patcher.get_int_list(this_patch_list)
			current_patch_index = len(this_int_patch_list) - 1
		elif current_patch_index > len(this_int_patch_list):
			# next file
			current_patch_index = 0
			current_file_index += 1

		if current_file_index >= len(performance_files):
			if preferences.get_preference_value("loop_performance_mode"):
				current_file_index = 0
			else:
				current_file_index = len(performance_files) - 1
		elif current_file_index < 0:
			if preferences.get_preference_value("loop_performance_mode"):
				current_file_index = len(performance_files) - 1
			else:
				current_file_index = 0
	outport.close()


def menu(stdscr: curses.window):
	stdscr.erase()
	create_needed_files()

	fix_screen_size(stdscr)

	while True:
		stdscr.refresh()
		options = ["Select MIDI port", "Performance Mode", "Open program data", "Patch/Config editing", "Settings", "Exit"]
		index, option = select_options(options,
									   "Welcome to MIDI-CONTROLLER!\nWhat would you like to do?", ">", 0)
		stdscr.erase()
		if index == 0:
			port_options()
		elif index == 1:
			performance_mode(stdscr)
		elif index == 2:
			open_program_data(stdscr)
		elif index == 3:
			patch_editing_page(stdscr)
		elif index == 4:
			preferences_page(stdscr)
		elif index == 5:
			break


if __name__ == "__main__":
	try:
		wrapper(menu)
	except KeyboardInterrupt:
		run_command(Command.CLEAR_SCREEN, [])
		exit(0)
