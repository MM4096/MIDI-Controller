import os
from enum import Enum

from modules.os_checker import get_os, Platform
from modules.preferences import get_preference, get_preference_value


class Command(Enum):
    WRITE_FILE = 0,
    OPEN_DIRECTORY = 1,


def run_command(command_type: Command, args):
    command_str = ""
    os_type = get_os()
    if os_type == Platform.WINDOWS:
        if command_type == Command.WRITE_FILE:
            command_str = f"/win_nano/nano.exe {args}"
        elif command_type == Command.OPEN_DIRECTORY:
            command_str = f"start {args}"
    elif os_type == Platform.LINUX:
        if command_type == Command.WRITE_FILE:
            if get_preference_value("linux_use_gedit_as_text_editor"):
                command_str = f"gedit {args}"
            else:
                command_str = f"nano {args}"
        elif command_type == Command.OPEN_DIRECTORY:
            command_str = f"xdg-open {args}"

    return os.system(command_str)
