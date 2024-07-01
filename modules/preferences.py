import json
import os
import time
from enum import Enum
from typing import Any

from modules import file_manager


class CustomSortingRules(Enum):
    NONE = 0,
    SORT_BY_NUMBERED_LIST = 1,
    SORT_BY_NUMBERED_LIST_LAST = 2,


class Preference:
    def __init__(self, preference_name: str = "", variable_type: Any = bool, initial_value: Any = False,
                 description: str = ""):
        self.preference_name = preference_name
        self.variable_type = variable_type
        if isinstance(initial_value, variable_type):
            self.value = initial_value
        else:
            self.value = self.get_initial_value(variable_type)
        self.description = description

    def toJSON(self):
        return {
            "preference_name": self.preference_name,
            "value": self.value,
            "description": self.description
        }

    @staticmethod
    def from_json(preference: dict):
        return Preference(preference["preference_name"], type(preference["value"]), preference["value"],
                          preference["description"])

    @staticmethod
    def to_json_array(preference_array: list):
        result = []
        for i in preference_array:
            if isinstance(i, Preference):
                result.append(i.toJSON())
        return result

    @staticmethod
    def to_preference_list(json_string: str):
        result = []
        data = json.loads(json_string)
        for i in data:
            result.append(Preference.from_json(i))
        return result

    @staticmethod
    def get_initial_value(_type):
        if isinstance(_type, (int, float)):
            return 0
        elif isinstance(_type, bool):
            return False
        elif isinstance(_type, dict):
            return {}
        else:
            return ""


# OUTDATED PREFERENCES DEFINITIONS
#  preferences = {
#     "save_midi_port": False,
#     "save_midi_through_port": False,
#     "update_patches_during_performance": False,
#     "print_logs": False,
#     "use_textbox_inputs": False,
#     "use_emacs_text_editor_for_inputs": False,
#     "skip_performance_mode_info": False,
#     "linux-use-gedit-as-text-editor": False,
#     "custom-sorting-rule": 0,
# }

initial_preferences = [
    Preference("save_midi_port", bool, False, "Whether the selected MIDI port should be saved "
                                              "between sessions"),
    Preference("save_midi_through_port", bool, False, "Only applies if `save_midi_port` is `true`."
                                                      "<br>Specifies whether the MIDI-Through port should be saved."),
    Preference("update_patches_during_performance", bool, True,
               "If the patch file is updated during Performance Mode, should the list be"
               " updated in real-time?"),
    Preference("use_emacs_text_editor_for_inputs", bool, False,
               "Whether to use an EMACS-style text editor for input prompts"),
    Preference("skip_performance_mode_info", bool, False,
               "Skip information on how to use performance mode [NOT RECOMMENDED FOR NEWER USERS]"),
    Preference("linux_editor_command", str, "nano",
               "[LINUX ONLY] command to for text editor (default: nano, example: gedit)"),
    Preference("default_preset", str, "",
               "Specify the default preset to load on patch create. Leave blank for nothing"),
    Preference("only_require_one_press_for_next_patch", bool, False,
               "Only require one [NEXT] press to go to the next patch in Performance Mode? (default is 2)"),
    Preference("allow_backtracking_in_performance_mode", bool, False,
               "Allow moving back a patch in Performance Mode with the [BEFORE] key?"),
    Preference("loop_performance_mode", bool, False,
               "Loop the performance mode list upon reaching the last patch? (Also applies to first patch and "
               "the [BEFORE] key if [allow_backtracking_in_performance_mode] is enabled)"),
]


def update_preferences() -> list[Preference]:
    file = file_manager.get_user_data_dir() + "/preferences"
    if not os.path.exists(file):
        file_manager.write_data(json.dumps(Preference.to_json_array(initial_preferences), indent=4), file)
        return initial_preferences
    else:
        return_val = []
        with open(file, "r") as f:
            data = Preference.to_preference_list(f.read())
            for init_preference in initial_preferences:
                found = False
                for preference in data:
                    if preference.preference_name == init_preference.preference_name:
                        found = True
                if not found:
                    data.append(init_preference)
                    return_val.append(init_preference)

            file_manager.write_data(json.dumps(Preference.to_json_array(data), indent=4), file)
        return return_val


def get_all_preferences() -> list[Preference]:
    file = file_manager.get_user_data_dir() + "/preferences"
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return Preference.to_preference_list(f.read())


def get_preference(key) -> Preference:
    for preference in get_all_preferences():
        if preference.preference_name == key:
            return preference
    return Preference(f"{key}", bool, False)


def get_preference_value(key):
    return get_preference(key).value


def set_preferences(preference_list: list):
    file = file_manager.get_user_data_dir() + "/preferences"
    with open(file, "w") as write:
        write.write(json.dumps(Preference.to_json_array(preference_list), indent=4))


def set_preference(key, value):
    preference_list = get_all_preferences()
    found_match = False
    for i in preference_list:
        if i.preference_name == key:
            i.value = value
            found_match = True
            break
    if not found_match:
        preference_list.append(Preference(key, type(value), value, "User-created preference"))
    set_preferences(preference_list)
