import json
import os

import file_manager
import logs

preferences = {
    "save_midi_port": False,
    "save_midi_through_port": False,
    "print_logs": False,
    "use_textbox_inputs": False,
    "use_emacs_text_editor_for_inputs": False,
    "skip_performance_mode_info": False,
}


def update_preferences():
    file = file_manager.get_user_data_dir() + "/preferences.json"
    # logs.write_log(file)
    if not os.path.exists(file):
        file_manager.write_data(json.dumps(preferences, indent=4), file)
    else:
        with open(file, "r") as f:
            data = json.loads(f.read())
            for key in preferences:
                if key not in data:
                    data[key] = preferences[key]
            file_manager.write_data(json.dumps(data, indent=4), file)


def get_preference(key):
    file = file_manager.get_user_data_dir() + "/preferences.json"
    if not os.path.exists(file):
        return preferences[key]
    with open(file, "r") as f:
        try:
            data = json.loads(f.read())
            return data[key]
        except KeyError:
            return preferences[key]
