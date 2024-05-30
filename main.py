import json
import subprocess
import threading

import keyboard
import mido
import mido.backends.rtmidi
import platformdirs
import os
import json_default
import custom_logging
from pick import pick
from file_manager import *
import patcher
import tools
from sys import exit

# region vars
selected_port = ""

# endregion


def can_use_keyboard_module() -> bool:
    try:
        keyboard.is_pressed("space")
        return True
    except ImportError:
        return False


def set_up_files():
    user_data_dir = get_user_data_dir()
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    if not os.path.exists(user_data_dir + "/patches/presets"):
        os.makedirs(user_data_dir + "/patches/presets")
    if not os.path.exists(user_data_dir + "/main_port.data"):
        with open(user_data_dir + "/main_port.data", "w") as f:
            f.write("")
    if not os.path.exists(user_data_dir + "/temp"):
        os.makedirs(user_data_dir + "/temp")
    json_default.write_main_json_file(user_data_dir, "config.json")
    custom_logging.set_logging_status(json_default.grab_key(user_data_dir, "config.json", "print_logs"))


def get_main_port():
    with open(get_file_path("main_port.data"), "r") as f:
        return f.read()


def set_main_port(_port: str):
    if json_default.grab_key(get_user_data_dir(), "config.json", "save_midi_port"):
        if "Midi Through" in _port:
            pass
        else:
            with open(get_file_path("main_port.data"), "w") as f:
                f.write(_port)


def get_ports():
    return mido.get_input_names()


def port_options():
    ports = get_ports()

    # see if saved port is available
    main_port = get_main_port()
    if main_port in ports:
        print(f"Connecting to {main_port} (previously saved port)")
        return main_port
    _port, index = pick(ports, "Pick a port to connect to: ", indicator=">")
    os.system("clear")
    print("Connecting to " + _port)
    set_main_port(_port)
    return _port


def open_program_data():
    os.system("clear")
    options = ["Open patches folder", "Open MIDI-Controller-linux folder", "Open config file for editing (requires [gedit])", "Back"]
    option, index = pick(options, "What would you like to open?", indicator=">")
    if index == 1:
        os.system(f"nautilus {get_user_data_dir()} &")
        # subprocess.Popen(["nautilus", get_user_data_dir()], text=False, stdout=subprocess.PIPE)
    elif index == 0:
        os.system(f"nautilus {get_user_data_dir()}/patches &")
    elif index == 2:
        os.system(f"gedit {get_user_data_dir()}/config.json &")
    else:
        return


def get_files_in_folder(path: str, filter_extension: str = "") -> list:
    if not os.path.exists(path):
        return []
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    if filter_extension != "":
        files = [f"{path}/{f}" for f in files if f.endswith(filter_extension)]
    return files


def get_folders_in_folder(path: str) -> list:
    if not os.path.exists(path):
        return []
    directories = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    return directories


def config_updater(previous_config: dict, allow_preset_additions: bool = False) -> dict:
    should_exit = False
    while not should_exit:
        os.system("clear")
        # grab keys from previous_config
        this_options = []
        for i in previous_config:
            this_options.append(i)

        # ask for new stuff
        given_options = this_options.copy()
        given_options += ["Create new entry", "Exit"]
        if allow_preset_additions:
            given_options.append("Add preset")
        option, index = pick(given_options, "Select something to edit", indicator=">")
        if index < len(this_options):
            # editing previous key
            key = option
            value = previous_config[option]
            stop_editing = False
            while not stop_editing:
                edit_options = [f"Edit key (was: [{key}])", f"Edit value (was: [{value}])", "Back"]
                selected_edit, selected_index = pick(edit_options, "What would you like to edit?")
                os.system("clear")
                if selected_index == 0:
                    new_key = input(f"Enter the new key (was: [{key}]):\n")
                    del previous_config[key]
                    previous_config[new_key] = value
                elif selected_index == 1:
                    new_value = input(f"Enter the new value (was: [{key}]):\n")
                    previous_config[key] = new_value
                else:
                    stop_editing = True
        else:
            new_index = index - len(this_options)
            if new_index == 0:
                is_correct = False
                os.system("clear")
                while not is_correct:
                    new_key = input("Enter a new key (CANCEL to cancel):\n")
                    new_value = input("Enter a new value:\n")
                    if new_key.lower() == "cancel":
                        break
                    try:
                        new_value = int(new_value)
                        previous_config[new_key] = new_value
                        is_correct = True
                    except:
                        # was not int
                        print("ERROR: given value was not an integer. Press [ENTER] to continue")
                        input()
            elif new_index == 1:
                return previous_config
            elif new_index == 2:
                if allow_preset_additions:
                    os.system("clear")
                    preset_name = input("Enter the name of the preset to add:\n")
                    preset_path = f"{get_user_data_dir()}/patches/presets/{preset_name}.midiconfig"
                    if not os.path.exists(preset_path):
                        print("ERROR: Preset does not exist. Press [ENTER] to continue")
                        input()
                    else:
                        previous_config["preset"] = preset_name
                else:
                    print("ERROR: Preset additions are not allowed. Press [ENTER] to continue")
                    input()


def create_patch():
    patch_list = []
    patch_config = {}
    patch_name = ""
    os.system("clear")
    #region previous
    # path = input("Enter the path to the patch file (type 'CANCEL' to cancel, type 'HELP' for help): \n")
    # if path.lower() == "cancel" or path.lower() == "":
    #     return
    # if path.lower() == "help":
    #     print("---HELP---\n"
    #           "Enter your patch name here. This will be the name of the patch file.\n"
    #           "You can also put folders here, so entering {example}/{name} will create the patch file at [appdata]/"
    #           "patches/{example}/{name}.midipatch\n"
    #           "The .midipatch extension DOES NOT need to be added.\n"
    #           "Press [ENTER] to continue")
    #     input()
    #     create_patch()
    #endregion
    stop = False
    current_directory = get_user_data_dir() + "/patches"
    path = ""
    while not stop:
        sections = current_directory.split("/")
        options = [".."]
        directories = get_folders_in_folder(current_directory)
        files = get_files_in_folder(current_directory, ".midipatch")
        options += [f"/{i}" for i in directories]
        options += [i.split("/")[-1] for i in files]
        options += ["Create a New Patch Here", "Cancel"]

        option, index = pick(options, "Select a patch", indicator=">")
        if index == 0:
            if not os.path.samefile(current_directory, get_user_data_dir()):
                sections.pop()
                current_directory = "/".join(sections)
        else:
            index -= 1
            if index < len(directories):
                sections.append(directories[index])
                current_directory = "/".join(sections)
            else:
                index -= len(directories)
                if index < len(files):
                    selected_file = files[index]
                    path = f"{selected_file}"
                    stop = True
                else:
                    index -= len(files)
                    if index == 0:
                        os.system("clear")
                        patch_name = input("What would you like to name the new patch?\n")
                        path = f"{current_directory}/{patch_name}.midipatch"
                        stop = True
                    else:
                        return

    absolute_path = path
    if os.path.exists(absolute_path):
        options = ["Edit", "Cancel"]
        option, index = pick(options, "Patch already exists. Edit patch?", indicator=">")
        if index == 0:
            patch_list = patcher.get_patch_list(absolute_path)
            patch_config = patcher.get_config_list_from_patch(absolute_path)
        else:
            create_patch()

    options = ["Update patch list (external editor [gedit])", "Update patch config", "Back"]
    option, index = pick(options, "Select an option", indicator=">")
    if index == 0:
        available_presets = patcher.get_available_presets(absolute_path)
        available_presets.pop(0)
        available_presets[0] = "\n\t# " + available_presets[0]
        file_data = ("# edit patches here. Either [string] (referring to a patch config) or [int] "
                     "(referring to that item) is allowed\n"
                     "# comments start with [#] \n\n"
                     "# Enter the patch name on the next line\n\n"
                     f"{path.split("/")[-1]}\n\n"
                     f"\t# Here's the usable presets. To add more, edit the [CONFIG] section.\n"
                     f"{'\n\t# '.join(available_presets)}\n\n"
                     "# Leave the next line the way it currently is\n"
                     "startlist\n"
                     "# start patching here\n")
        file_data += "\n".join(patch_list)
        with open(f"{get_user_data_dir()}/temp/patch_list.temp", "w") as f:
            f.write(file_data)
        os.system(f"gedit {get_user_data_dir()}/temp/patch_list.temp")
        with open(f"{get_user_data_dir()}/temp/patch_list.temp", "r") as f:
            given_list = f.read().splitlines()
        os.remove(f"{get_user_data_dir()}/temp/patch_list.temp")
        patch_list.clear()
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
    elif index == 1:
        patch_config = config_updater(patch_config, allow_preset_additions=True)
    else:
        return

    compiled_data = patcher.compile_patch(patch_config, patch_list, patch_name)
    patcher.write_data(compiled_data, absolute_path)
    create_patch()


def create_config():
    os.system("clear")
    config_list = {}

    path = ""
    current_directory = get_user_data_dir() + "/patches/presets"
    stop = False
    while not stop:
        split_path = current_directory.split("/")
        options = [".."]
        directories = get_folders_in_folder(current_directory)
        files = [i.split("/")[-1] for i in get_files_in_folder(current_directory, ".midiconfig")]
        options += [f"/{i}" for i in directories]
        options += files
        options += ["Create a new Config here", "Cancel"]

        option, index = pick(options, "Select a patch", indicator=">")
        if index == 0:
            if not os.path.samefile(current_directory, get_user_data_dir()):
                split_path.pop()
                "/".join(current_directory)
        else:
            index -= 1
            if index < len(directories):
                split_path.append(directories[index])
            else:
                index -= len(directories)
                if index < len(files):
                    path = f"{current_directory}/{files[index]}"
                    stop = True
                else:
                    index -= len(files)
                    if index == 0:
                        new_file = input("Name your config file:\n")
                        path = f"{current_directory}/{new_file}.midiconfig"
                        stop = True
                    else:
                        return

    absolute_path = path
    if os.path.exists(absolute_path):
        options = ["Edit", "Cancel"]
        option, index = pick(options, "Config already exists. Edit config?", indicator=">")
        if index == 0:
            config_list = patcher.parse_preset(absolute_path)
            pass
        else:
            create_config()
    config_list = config_updater(config_list)
    patcher.write_data(json.dumps(config_list), absolute_path)


def edit_patches():
    os.system("clear")
    options = ["Create/Edit patches", "Create/Edit patch configs", "Back"]
    option, index = pick(options, "What would you like to do?", indicator=">")
    if index == 0:
        create_patch()
    elif index == 1:
        create_config()
    else:
        return
    edit_patches()


def select_file(path: str, maximum_back_path: str = "", allowed_extensions: str = "") -> str:
    if not os.path.exists(path):
        return ""
    selected_file = False
    current_path = path.split("/")
    while not selected_file:
        os.system("clear")
        this_directory = "/".join(current_path)
        files = get_files_in_folder(this_directory, allowed_extensions)
        files = [f.split("/")[-1] for f in files]
        folders = [f for f in os.listdir(this_directory) if os.path.isdir(os.path.join(this_directory, f))]
        display_folders = [f"/{f}" for f in folders]
        options = []
        if not os.path.samefile(this_directory, maximum_back_path):
            options += [".."]
        options += display_folders + files
        options.append("Cancel")
        option, index = pick(options, f"Select a file in {this_directory}", indicator=">")
        option = option.replace("/", "")
        if option == "..":
            current_path.pop()
        elif option == "Cancel":
            return ""
        else:
            if option in files:
                return f"{this_directory}/{option}"
            else:
                current_path.append(option)


def select_folder(path: str, maximum_back_path: str = "") -> str:
    if not os.path.exists(path):
        return ""
    selected_folder = False
    current_path = path.split("/")
    while not selected_folder:
        os.system("clear")
        this_directory = "/".join(current_path)
        folders = [f for f in os.listdir(this_directory) if os.path.isdir(os.path.join(this_directory, f))]
        display_folders = [f"/{f}" for f in folders]
        options = []
        if not os.path.samefile(this_directory, maximum_back_path):
            options += [".."]
        options += display_folders
        options += ["Select", "Cancel"]
        option, index = pick(options, f"Select a folder in {this_directory}", indicator=">")
        option = option.replace("/", "")
        if option == "..":
            current_path.pop()
        elif option == "Cancel":
            return ""
        elif option == "Select":
            return "/".join(current_path)
        else:
            current_path.append(option)


def file_selection_performance_mode() -> list:
    performance_files = []
    stop_file_selection = False
    while not stop_file_selection:
        os.system("clear")
        options = ["Perform a single patch", "Perform a list of patches (in folder)", "Back"]
        option, index = pick(options, "What would you like to do?", indicator=">")
        if index == 0:
            # file selection
            selected_file = select_file(get_user_data_dir(), get_user_data_dir(), ".midipatch")
            if selected_file == "":
                continue
            performance_files.append(selected_file)
        elif index == 1:
            selected_folder = select_folder(get_user_data_dir(), get_user_data_dir())
            if selected_folder == "":
                continue
            performance_files = get_files_in_folder(selected_folder, ".midipatch")

        stop_file_selection = True
    return performance_files


def display_patch_info(path: str, selected_patch_index: int = 0, next_patch_name: str = ""):
    os.system("clear")
    data = patcher.parse_patch_from_file(path)
    print(f"Patch Name: {data['patch_name']}")
    patch_list = patcher.get_patch_list(path)
    print("Patch List:")
    for i in range(len(patch_list)):
        if i == selected_patch_index:
            print(f" >  {patch_list[i]}")
        else:
            print(f"    {patch_list[i]}")
    if selected_patch_index >= len(patch_list):
        print(f" >  [END OF PATCH LIST]")
    else:
        print(f"    [END OF PATCH LIST]")
    if next_patch_name != "":
        print(f"Next Patch: {next_patch_name}")


pedal_pressed = False
def wait_for_switch_pedal(port: str):
    with mido.open_input(port) as inport:
        for msg in inport:
            if msg.type == "control_change" and msg.control == 82 and msg.value > 10:
                pedal_pressed = True
                return


def performance_mode():
    performance_files = []
    os.system("clear")
    print("Welcome to Performance Mode!\nTo exit, press [CTRL+C]\nPress [ENTER] to continue")
    input()
    os.system("clear")
    available_ports = get_ports()
    preferred_port = get_main_port()
    if preferred_port in available_ports:
        print(f"Connecting to {preferred_port} (previously saved port)")
    else:
        print("No port selected. Please select a port.")
        preferred_port = port_options()

    finalized_files = False
    while not finalized_files:
        performance_files = file_selection_performance_mode()
        if performance_files == [] or performance_files == [""]:
            return
        os.system("clear")
        print("Here is a list of patches to perform. Is this OK? (Y/n)\n")
        print("\n".join(performance_files))
        option = input()
        if option.lower() == "y" or option.lower() == "":
            finalized_files = True
        else:
            pass
    os.system("clear")
    option, selected_index = pick([i.split("/")[-1].replace(".midipatch", "") for i in performance_files],
                                  "Select a patch to start with", indicator=">")

    option, index = pick(["[ENTER] key", "Switch Pedal"], "Select switch type", indicator=">")
    using_switch_pedal = index == 1

    print(f"Performance mode is calibrated with {'SWITCH PEDAL' if using_switch_pedal else '[ENTER]'} as [Next Patch]."
          "\nTo leave Performance Mode, press [CTRL + C]."
          "\nCurrently, the loop mode is set to [LOOP]."
          f"{'' if not using_switch_pedal else '\nMake sure your pedal is set up properly: Go to [GLOBAL/MEDIA]>'
                                               '[G-INPUT/CTRL]>[Foot SW Assign] and set to [Foot Switch]'}"
          "\nPress [ENTER] to continue")
    input()
    with mido.open_output(preferred_port) as outport:
        current_file_index = selected_index
        current_patch_index = 0
        cached_index = -1
        while True:
            current_file_path = performance_files[current_file_index]
            this_patch_list = patcher.parse_patch_from_file(current_file_path)
            this_int_patch_list = patcher.get_int_list(this_patch_list)

            next_file_path = performance_files[current_file_index + 1] if current_file_index + 1 < len(
                performance_files) else performance_files[0]
            next_patch_name = patcher.parse_patch_from_file(next_file_path)["patch_name"]
            if cached_index != current_patch_index:
                clamped_index = tools.clampi(current_patch_index, 0, len(this_int_patch_list) - 1)
                # print("Sending output!")
                outport.send(mido.Message("program_change", program=this_int_patch_list[clamped_index]))
                # input()
                cached_index = current_patch_index
                display_patch_info(current_file_path, current_patch_index, next_patch_name)
            change_direction = 1
            if using_switch_pedal:
                global pedal_pressed
                pedal_pressed = False
                thread = threading.Thread(target=wait_for_switch_pedal, args=preferred_port)
                thread.start()
                while not pedal_pressed:
                    if can_use_keyboard_module():
                        if keyboard.is_pressed("up_arrow"):
                            change_direction = -1
                            break
            else:
                if can_use_keyboard_module():
                    stop = False
                    while not stop:
                        if keyboard.is_pressed("up_arrow"):
                            change_direction = -1
                            stop = True
                        elif keyboard.is_pressed("enter") or keyboard.is_pressed("space"):
                            stop = True
                else:
                    response = input()
                    if len(response) > 1:
                        change_direction = -1
            current_patch_index += change_direction
            if current_patch_index < 0:
                current_patch_index = 0
            if current_patch_index > len(this_int_patch_list):
                current_patch_index = 0
                current_file_index += 1
                if current_file_index >= len(performance_files):
                    current_file_index = 0


def main_menu():
    os.system("clear")
    title = "Welcome! What would you like to do?"
    options = ["Select MIDI port", "Performance Mode", "Open program data", "Patch editing",
               "Exit"]
    option, index = pick(options, title, indicator=">")
    if index == 0:
        port_options()
        main_menu()
    elif index == 1:
        performance_mode()
        main_menu()
    elif index == 2:
        open_program_data()
        main_menu()
    elif index == 3:
        edit_patches()
        main_menu()
    elif index == 4:
        exit(0)


if "__main__" == __name__:
    try:
        os.system("clear")
        set_up_files()
        main_menu()
    except KeyboardInterrupt:
        os.system("clear")
        print("Quitting!")
        exit(0)
    # port = port_options()
    # with mido.open_output(port) as outport:
    #     outport.send(mido.Message("program_change", program=17))
