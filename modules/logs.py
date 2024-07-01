from modules import file_manager


def write_log(data: str):
    with open(file_manager.get_user_data_dir() + "/logs.txt", "a") as file:
        file.write(data + "\n")
