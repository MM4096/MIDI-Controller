import json
import os
import custom_logging

default_json_data = {
    "save_midi_port": False,
    "save_midi_through_port": False,
    "print_logs": False,
}


def write_main_json_file(path, filename):
    if os.path.exists(path + "/" + filename):
        with open(path + "/" + filename, "r") as f:
            if json.loads(f.read()) == default_json_data:
                return
    with open(path + "/" + filename, "w") as f:
        f.write(json.dumps(default_json_data))


def grab_info(path, filename):
    with open(path + "/" + filename, "r") as f:
        return json.loads(f.read())


def grab_key(path, filename, key):
    return grab_info(path, filename)[key]
