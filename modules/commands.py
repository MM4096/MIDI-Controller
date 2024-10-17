import file_manager

def get_output_directory() -> str:
	return f"{file_manager.get_user_data_dir()}/output.txt"
