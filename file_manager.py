import os.path

import platformdirs


def get_user_data_dir() -> str:
    return platformdirs.user_data_dir("MIDI-Controller", "mm4096")


def get_file_path(file_name) -> str:
    return get_user_data_dir() + "/" + file_name


def write_data(data: str, file_path: str):
    if os.path.exists(file_path):
        print("Overwriting")
    split_path = file_path.split("/")
    split_path.pop(-1)
    if not os.path.exists("/".join(split_path)):
        os.makedirs("/".join(split_path))
    with open(file_path, "w") as file:
        file.write(data)
