import platform
from enum import Enum


class Platform(Enum):
    NONE = 0,
    LINUX = 1,
    MACOS = 2,
    WINDOWS = 3


def get_os() -> Platform:
    detect = platform.system()
    if detect == "Linux":
        return Platform.LINUX
    elif detect == "Windows":
        return Platform.WINDOWS
    elif detect == "Darwin":
        return Platform.MACOS
    return Platform.NONE
