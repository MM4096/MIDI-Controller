import os.path

import platformdirs


def get_user_data_dir() -> str:
    return platformdirs.user_data_dir("MIDI-Controller", "mm4096")


def get_file_path(file_name) -> str:
    return get_user_data_dir() + "/" + file_name

def get_patch_directory() -> str:
    return get_user_data_dir() + "/" + "patches"

def get_config_directory() -> str:
    return get_user_data_dir() + "/" + "configs"


def write_data(data: str, file_path: str):
    if os.path.exists(file_path):
        pass
    split_path = file_path.split("/")
    split_path.pop(-1)
    if not os.path.exists("/".join(split_path)):
        os.makedirs("/".join(split_path))
    with open(file_path, "w") as file:
        file.write(data)


def create_dir_if_not_exists(file_path: str):
    if not os.path.exists(file_path):
        os.makedirs(file_path)


def get_files_in_dir(directory: str) -> list:
    return [i for i in os.listdir(directory) if os.path.isfile(os.path.join(directory, i))]


def get_dirs_in_dir(directory: str) -> list:
    return [i for i in os.listdir(directory) if os.path.isdir(os.path.join(directory, i))]

def remove_patch_directory_from_patch(patch_path: str):
    return patch_path.replace(get_patch_directory() + "/", "")

def get_patch_directory_from_patch(patch_path: str):
    return get_patch_directory() + "/" + patch_path