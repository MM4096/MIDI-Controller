import file_manager
from os.path import join as path_join

def get_output_file() -> str:
	return file_manager.get_file_path("output.txt")

def get_command_file() -> str:
	return file_manager.get_file_path("commands.txt")