from enum import Enum

logging_status = False


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class LogType(Enum):
    NONE = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    SUCCESS = 4


def set_logging_status(status: bool):
    global logging_status
    logging_status = status


def log(message: str, log_type: LogType = LogType.NONE, sender: str = "", skip_logging: bool = False):
    if sender != "":
        message = f"[{sender}] {message}"
    if logging_status or skip_logging:
        if log_type == LogType.NONE:
            print(message)
        if log_type == LogType.INFO:
            print(f"{bcolors.OKBLUE}{message}{bcolors.ENDC}")
        elif log_type == LogType.WARNING:
            print(f"{bcolors.WARNING}{message}{bcolors.ENDC}")
        elif log_type == LogType.ERROR:
            print(f"{bcolors.FAIL}{message}{bcolors.ENDC}")
        elif log_type == LogType.SUCCESS:
            print(f"{bcolors.OKGREEN}{message}{bcolors.ENDC}")


def print_error(message: str, sender: str = "", skip_logging: bool = False):
    log(message, LogType.ERROR, sender, skip_logging)


def print_warning(message: str, sender: str = "", skip_logging: bool = False):
    log(message, LogType.WARNING, sender, skip_logging)
