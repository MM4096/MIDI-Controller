import json
import os

from modules import file_manager
from modules import tools

null_parse = {}


def parse_patch(patch_info: str) -> dict:
    # parser removes newlines and comments in this stage.
    # if anyone has a better method of doing this, please let me know.
    lines = patch_info.splitlines()
    final_lines = []
    for line in lines:
        removed_spaces = line.replace(" ", "")
        if removed_spaces == "":
            pass
        elif removed_spaces[0] == "#":
            pass
        else:
            final_lines.append(line)

    config_lines = []
    started_config_search: bool = False

    list_lines = []
    started_list_search: bool = False

    removed_config_data_lines = final_lines.copy()

    for line in final_lines:
        if line.lower() == "startconfig":
            started_config_search = True
        elif line.lower() == "endconfig":
            started_config_search = False
            removed_config_data_lines.remove(line)
        elif line.lower() == "startlist":
            started_list_search = True
        elif line.lower() == "endlist":
            started_list_search = False
            removed_config_data_lines.remove(line)

        if started_config_search and started_list_search:
            # custom_logging.print_error("Error: startconfig and startlist were found at the same time.",
            #                     "Patch Parser", skip_custom_logging=True)
            return null_parse

        if started_config_search:
            config_lines.append(line)
            removed_config_data_lines.remove(line)
        elif started_list_search:
            list_lines.append(line)
            removed_config_data_lines.remove(line)

    config_lines.pop(0)
    list_lines.pop(0)

    if started_config_search:
        # custom_logging.print_error("Error: startconfig was found but endconfig was not found.", "Patch Parser",
        #                     skip_custom_logging=True)
        return null_parse
    elif started_list_search:
        # custom_logging.print_error("Error: startlist was found but endlist was not found.", "Patch Parser",
        #                     skip_custom_logging=True)
        return null_parse

    # finally, values
    patch_name = "MIDI Patcher patch" if len(removed_config_data_lines) == 0 else removed_config_data_lines[0]
    patch_config = json.loads("\n".join(config_lines))
    patch_list = json.loads("\n".join(list_lines))
    return {
        "patch_name": patch_name,
        "patch_config": patch_config,
        "patch_list": patch_list
    }


def parse_patch_from_file(file_path: str) -> dict:
    with open(file_path, "r") as file:
        _patch_info = file.read()
    return parse_patch(_patch_info)


def parse_preset(filepath: str) -> dict:
    """
    Parse a .midiconfig file given by {filepath}, returning a dictionary of presets.

    If {filepath} does not contain the .midiconfig extension, this function will add that extension
    """
    if ".midiconfig" not in filepath:
        filepath += ".midiconfig"
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r") as file:
        contents = file.read()
        lines = contents.splitlines()
        final_lines = []
        for line in lines:
            removed_spaces = line.replace(" ", "")
            if removed_spaces == "":
                pass
            elif removed_spaces[0] == "#":
                pass
            else:
                final_lines.append(line)
        return json.loads("\n".join(final_lines))


def get_patch_list(file_path: str) -> list:
    data = parse_patch_from_file(file_path)
    return data["patch_list"]["list"]


def get_config_list_from_patch(file_path: str) -> dict:
    data = parse_patch_from_file(file_path)
    return data["patch_config"]


def get_available_presets(path: str) -> list:
    if not os.path.exists(path):
        return []
    patch_config = get_config_list_from_patch(path)
    if "preset" in patch_config:
        preset = patch_config["preset"]
        preset_path = f"{file_manager.get_user_data_dir()}/presets/{preset}.midiconfig"
        result = parse_preset(preset_path)
        for key in result:
            patch_config[key] = result[key]
    result = []
    for key in patch_config:
        result.append(key)
    return result


def get_int_list(data: dict) -> list:
    patch_config = data["patch_config"]
    patch_list = data["patch_list"]
    if "preset" in patch_config:
        preset = patch_config["preset"]
        preset_path = f"{file_manager.get_user_data_dir()}/presets/{preset}.midiconfig"
        result = parse_preset(preset_path)
        for key in result:
            patch_config[key] = result[key]

    final_int_list = []
    if "list" in patch_list:
        for obj in patch_list["list"]:
            if isinstance(obj, dict):
                if tools.is_int(obj["sound"]):
                    final_int_list.append(int(obj["sound"]))
                elif obj["sound"] in patch_config:
                    final_int_list.append(patch_config[obj["sound"]])
                else:
                    final_int_list.append(0)
    else:
        return []
    return final_int_list


def get_comment_list(data: dict) -> list:
    patch_list = data["patch_list"]
    final_comment_list = []
    if "list" in patch_list:
        for obj in patch_list["list"]:
            if isinstance(obj, dict):
                final_comment_list.append(obj["comments"])
            else:
                final_comment_list.append("")
    else:
        return []
    return final_comment_list


def patch_return_int_list(file_path: str) -> list:
    data = parse_patch_from_file(file_path)
    return get_int_list(data)


def write_data(string: str, file_path: str):
    if os.path.exists(file_path):
        pass
    file_manager.write_data(string, file_path)


def compile_patch(config: dict, patch_list: list, patch_name: str) -> str:
    new_patch_list = {
        "list": patch_list
    }
    config_str = json.dumps(config, indent=4)
    list_str = json.dumps(new_patch_list, indent=4)
    return (f"# patch\n"
            f"{patch_name}\n"
            f"startconfig\n"
            f"{config_str}\n"
            f"endconfig\n"
            f"startlist\n"
            f"{list_str}\n"
            f"endlist")


def convert_legacy_format_to_new_format_sound_list(filepath: str):
    """
    Modifies the old patch list method of "array of sounds" to "array of dictionaries with sounds and comments"
    :param filepath: path of file to edit
    """
    current_data: dict = parse_patch_from_file(filepath)
    current_list: list = current_data["patch_list"]["list"]
    new_list: list = []
    for obj in current_list:
        if isinstance(obj, dict):
            new_list.append(obj)
        else:
            new_list.append({"sound": obj, "comments": ""})
    current_data["patch_list"]["list"] = new_list
    new_patch = compile_patch(current_data["patch_config"], current_data["patch_list"]["list"],
                              current_data["patch_name"])
    write_data(new_patch, filepath)


# Code for changes
# change "filepath" to your target path.
# leaving it blank searches all of `get_user_data_dir()`
filepath = "/"
if __name__ == "__main__":
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(file_manager.get_user_data_dir() + filepath)
             for f in filenames if os.path.splitext(f)[1] == '.midipatch']
    for index, i in enumerate(files):
        print(f"Editing {i} (File: {index + 1}/{len(files)})")
        convert_legacy_format_to_new_format_sound_list(i)
        print("Successful!")
