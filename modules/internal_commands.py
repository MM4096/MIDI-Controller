import os
from enum import Enum

from modules.os_checker import get_os, Platform
from modules.preferences import get_preference, get_preference_value


class Command(Enum):
    WRITE_FILE = 0,
    OPEN_DIRECTORY = 1,
    CLEAR_SCREEN = 2,


def run_command(command_type: Command, args):
    command_str = ""
    os_type = get_os()
    if os_type == Platform.WINDOWS:
        if command_type == Command.WRITE_FILE:
            command_str = f"/win_nano/nano.exe {args}"
        elif command_type == Command.OPEN_DIRECTORY:
            command_str = f"start {args}"
        elif command_type == Command.CLEAR_SCREEN:
            command_str = "cls"
    elif os_type == Platform.LINUX:
        if command_type == Command.WRITE_FILE:
            command_str = f"{get_preference_value('linux_editor_command')} {args}"
        elif command_type == Command.OPEN_DIRECTORY:
            command_str = f"xdg-open {args}"
        elif command_type == Command.CLEAR_SCREEN:
            command_str = "clear"

    return os.system(command_str)
