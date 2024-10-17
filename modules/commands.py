from enum import Enum

import file_manager
from os.path import join as path_join

class OutputType(Enum):
	PERFORMANCE_STARTED = 0,
	PERFORMANCE_PATCH_CHANGED = 1,
	PERFORMANCE_FILE_CHANGED = 2,
	PERFORMANCE_ENDED = 3,

COMMAND_SEPARATOR: str = "<~separator~>"


def get_output_file() -> str:
	return file_manager.get_file_path("output.txt")

def get_command_file() -> str:
	return file_manager.get_file_path("commands.txt")

def add_to_output(text: str) -> None:
	with open(get_output_file(), "a") as f:
		f.write(text + "\n")

def send_message(message_type: OutputType, contents: list | str = ""):
	message_name: str = ""
	if message_type == OutputType.PERFORMANCE_STARTED:
		message_name = "performance_started"
	elif message_type == OutputType.PERFORMANCE_PATCH_CHANGED:
		message_name = "performance_patch_changed"
	elif message_type == OutputType.PERFORMANCE_FILE_CHANGED:
		message_name = "performance_file_changed"
	elif message_type == OutputType.PERFORMANCE_ENDED:
		message_name = "performance_ended"

	contents_str: str = contents if isinstance(contents, str) else COMMAND_SEPARATOR.join(contents)

	add_to_output(f"{message_name}{COMMAND_SEPARATOR}{contents_str}\n")