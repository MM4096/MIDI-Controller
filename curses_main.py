import curses
import json
import multiprocessing
import os
import threading
from curses import wrapper
from curses.textpad import Textbox, rectangle
import mido
import mido.backends.rtmidi
import tools
import file_manager
import preferences
import patcher
import sys

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

KEY_UP = [65]
KEY_DOWN = [66]
KEY_ENTER = [10, 13]
KEY_BACKSPACE = [127, 263]
KEY_SPACE = [32]
KEY_ESCAPE = [27]

# endregion

pedal_pressed = False


def wait_for_switch_pedal(port: str):
    global pedal_pressed
    with mido.open_input(port) as inport:
        for msg in inport:
            if msg.type == "control_change" and msg.control == 82 and msg.value > 10:
                pedal_pressed = True
                return


def get_main_port():
    with open(file_manager.get_user_data_dir() + "/main_port.data", "r") as f:
        return f.read()


def set_main_port(_port: str):
    if preferences.get_preference("save_midi_port"):
        if "Midi Through" in _port:
            pass
        else:
            with open(file_manager.get_user_data_dir() + "/main_port.data", "w") as f:
                f.write(_port)


def get_ports():
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
    new_window = curses.newwin(2, max(max_length, len(title) + 2), 0, 0)
    new_window.erase()
    new_window.addstr(title + "\n")
    new_window.refresh()
    if preferences.get_preference("use_emacs_text_editor_for_inputs"):
        # create input box
        win = curses.newwin(1, max_length, 1, 0)
        box = Textbox(win)
        new_window.refresh()
        box.edit()
        return box.gather()
    else:
        # set cursor position to be inside box
        new_window.move(1, 0)
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


def create_needed_files():
    file_manager.create_dir_if_not_exists(file_manager.get_user_data_dir())
    file_manager.create_dir_if_not_exists(file_manager.get_user_data_dir() + "/patches")
    file_manager.create_dir_if_not_exists(file_manager.get_user_data_dir() + "/patches/presets")
    file_manager.create_dir_if_not_exists(file_manager.get_user_data_dir() + "/temp")
    preferences.update_preferences()


def set_cursor_visibility(visibility: bool):
    curses.curs_set(1 if visibility else 0)


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
        for i in range(len(options)):
            new_window.addstr(f"{not_selected_string if index != i else indicator} {options[i]}\n")
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


def open_program_data(stdscr: curses.window):
    while True:
        options = ["Open patches folder", "Open presets folder", "Open preferences file (requires gedit)", "Back"]
        index, option = select_options(options, "Open program data", ">", 0)
        stdscr.erase()
        if index == 0:
            os.system(f"xdg-open {file_manager.get_user_data_dir()}/patches")
        elif index == 1:
            os.system(f"xdg-open {file_manager.get_user_data_dir()}/patches/presets")
        elif index == 2:
            os.system(f"gedit {file_manager.get_user_data_dir()}/preferences.json")
        elif index == 3:
            break


def select_file(default_path: str, title: str = "Select a file!", allow_leaving_default_path: bool = False,
                filter_extension: str = ""):
    while True:
        split_path = default_path.split("/")
        directories = file_manager.get_dirs_in_dir(default_path)
        files = [i for i in file_manager.get_files_in_dir(default_path) if i.endswith(filter_extension)]

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
        options = [".."] + directory_display + ["Select Folder", "Back"]
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
        folder_path = select_directory(file_manager.get_user_data_dir() + "/patches/presets",
                                       "Select a folder to create the config in", False)
        if folder_path == "":
            edit_absolute_config(stdscr)
        else:
            name = create_input(50, "Enter the name of the new config")
            new_config = edit_config({}, False)
            file_manager.write_data(json.dumps(new_config), f"{folder_path}/{name}.midiconfig")
    else:
        config_path = select_file(file_manager.get_user_data_dir() + "/patches/presets", "Select a config file", True,
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
        folder_path = select_directory(file_manager.get_user_data_dir() + "/patches",
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
        patch_path = select_file(file_manager.get_user_data_dir() + "/patches", "Select a patch file", True,
                                 ".midipatch")
        if patch_path == "":
            edit_patch(stdscr)
    else:
        return

    while True:
        patch = patcher.parse_patch_from_file(patch_path)
        patch_name = patch["patch_name"]
        patch_config = patch["patch_config"]
        patch_list = patch["patch_list"]["list"]
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
                         "# start patching here\n")
            file_data += "\n".join(patch_list)
            with open(f"{file_manager.get_user_data_dir()}/temp/patch_list.temp", "w") as f:
                f.write(file_data)
            os.system(f"gedit {file_manager.get_user_data_dir()}/temp/patch_list.temp")
            with open(f"{file_manager.get_user_data_dir()}/temp/patch_list.temp", "r") as f:
                given_list = f.read().splitlines()
            os.remove(f"{file_manager.get_user_data_dir()}/temp/patch_list.temp")
            patch_list = []
            for line in given_list:
                removed_spaces = line.replace(" ", "").replace("\t", "")
                if removed_spaces == "":
                    pass
                elif removed_spaces[0] == "#":
                    pass
                else:
                    patch_list.append(line)
            list_copy = patch_list.copy()
            for line in list_copy:
                if line == "startlist":
                    patch_list.remove(line)
                    break
                else:
                    patch_name = line
                    patch_list.remove(line)
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


def performance_mode(stdscr: curses.window):
    performance_files = []
    stdscr.erase()
    stdscr.refresh()
    if not preferences.get_preference("skip_performance_mode_info"):
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
        index, option = select_options(["Perform a single patch", "Perform a list of patches from a folder", "Back"],
                                       "Performance Mode", ">", 0)
        if index == 0:
            patch_path = select_file(file_manager.get_user_data_dir() + "/patches", "Select a patch file", True,
                                     ".midipatch")
            if patch_path == "":
                continue
            performance_files = [patch_path]
            selected_files = True
        elif index == 1:
            folder_path = select_directory(file_manager.get_user_data_dir() + "/patches", "Select a folder", False)
            if folder_path == "":
                continue
            performance_files = [folder_path + "/" + i for i in file_manager.get_files_in_dir(folder_path) if
                                 i.endswith(".midipatch")]
            selected_files = True
        else:
            return
        list_of_files = [i.split("/")[-1].replace(".midipatch", "") for i in performance_files]
        stdscr.erase()
        stdscr.refresh()
        index, option = select_options(["Yes", "No"], "Here's a list of files to perform. Is this OK?"
                                                      "\n" + "\n".join(list_of_files), ">", 0)
        if index == 0:
            break
    index, option = select_options([i.split("/")[-1].replace(".midipatch", "") for i in performance_files],
                                   "Which patch would you like to start with?", ">", 0)

    stdscr.erase()
    stdscr.refresh()
    with mido.open_output(preferred_port) as outport:
        current_file_index = index
        current_patch_index = 0
        cached_index = -1
        stop = False
        while not stop:
            current_file_path = performance_files[current_file_index]
            this_patch_list = patcher.parse_patch_from_file(current_file_path)
            this_int_patch_list = patcher.get_int_list(this_patch_list)
            next_file_path = performance_files[current_file_index + 1] if current_file_index + 1 < len(
                performance_files) else performance_files[0]
            next_patch_name = patcher.parse_patch_from_file(next_file_path)["patch_name"]
            if cached_index != current_patch_index:
                cached_index = current_patch_index
                clamped_index = tools.clampi(current_patch_index, 0, len(this_int_patch_list) - 1)
                outport.send(mido.Message("program_change", program=this_int_patch_list[clamped_index]))
                # region display info
                stdscr.erase()
                current_file_name = patcher.parse_patch_from_file(current_file_path)["patch_name"]
                stdscr.addstr(f"Current patch: {current_file_name}\n")
                patch_list = patcher.parse_patch_from_file(current_file_path)["patch_list"]["list"]
                for i in range(len(patch_list)):
                    modifier = ">" if current_patch_index == i else " "
                    stdscr.addstr(f" {modifier}  {patch_list[i]}\n")
                if current_patch_index >= len(this_int_patch_list):
                    stdscr.addstr(" >  [END OF PATCH LIST]")
                else:
                    stdscr.addstr("    [END OF PATCH LIST]")
                stdscr.addstr(f"\n\nNext patch: {next_patch_name}\n")
                stdscr.refresh()
                # endregion

            direction = 1
            global pedal_pressed
            pedal_pressed = False
            process = multiprocessing.Process(target=wait_for_switch_pedal, args=[preferred_port])
            process.start()
            stdscr.nodelay(1)
            stdscr.timeout(100)
            while not pedal_pressed:
                this_input = stdscr.getch()
                if this_input in KEY_ENTER or this_input in KEY_SPACE:
                    direction = 1
                    break
                elif this_input in KEY_BACKSPACE or this_input in KEY_UP:
                    direction = -1
                    break
                elif this_input in KEY_ESCAPE:
                    stop = True
                    break
            process.kill()

            current_patch_index += direction
            if current_patch_index < 0:
                current_patch_index = 0
            elif current_patch_index > len(this_int_patch_list):
                # next file
                current_patch_index = 0
                current_file_index += 1
                if current_file_index >= len(performance_files):
                    current_file_index = 0


def menu(stdscr: curses.window):
    stdscr.erase()

    while True:
        stdscr.refresh()
        options = ["Select MIDI port", "Performance Mode", "Open program data", "Patch/Config editing", "Exit"]
        index, option = select_options(options,
                                       "Welcome to MIDI-CONTROLLER!\nWhat would you like to do?", ">", 0)
        stdscr.erase()
        if index == 0:
            pass
        elif index == 1:
            performance_mode(stdscr)
        elif index == 2:
            open_program_data(stdscr)
        elif index == 3:
            patch_editing_page(stdscr)
        elif index == 4:
            break


if __name__ == "__main__":
    create_needed_files()
    wrapper(menu)
    exit(0)
