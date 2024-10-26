import os
import re
from math import floor


def clamp(_n: float, _min: float, _max: float) -> float:
    """
    Clamp a number between a minimum and maximum value.
    :param _n:
    :param _min:
    :param _max:
    :return:
    """
    if _n < _min:
        return _min
    elif _n > _max:
        return _max
    else:
        return _n


def clampi(_n: int, _min: int, _max: int) -> int:
    """
    Clamp a number between a minimum and maximum value. Takes in integers only.
    :param _n:
    :param _min:
    :param _max:
    :return:
    """
    if _n < _min:
        return _min
    elif _n > _max:
        return _max
    else:
        return _n


def is_int(value: str) -> bool:
    """
    Checks whether a string is an integer
    :param value: the string to be evaluated
    :return: whether the string is an int or not
    """
    try:
        int(value)
        return True
    except ValueError:
        return False


def cut_array(array: list, cut_around: int, cut_amount: int = 15) -> (list, int):
    """
    Cuts an array into a given number, around a given amount
    :param array: the array to be cut
    :param cut_around: the number to perform the cut around (tries to center this value)
    :param cut_amount: the amount of items to return (init 15)
    :return: (cut array, starting index)
    """
    length: int = len(array)
    start = max(0, cut_around - cut_amount // 2)
    end = min(length, start + cut_amount)
    # modify start if end is ended
    start = max(0, end - cut_amount)

    return array[start:end], start


def is_sublist_with_more_elements(init_array: list, cut_array: list, start_cut_array_index: int) -> bool:
    # Check if cut_array is a sublist of init_array starting at start_cut_array_index
    if init_array[start_cut_array_index:start_cut_array_index + len(cut_array)] != cut_array:
        return False

    # Check if there are more elements after the cut_array
    if start_cut_array_index + len(cut_array) < len(init_array):
        return True
    else:
        return False


def is_recognized_boolean(value: str) -> bool:
    """
    Checks whether a string is a recognized boolean value
    :param value: the string to be evaluated
    :return: whether the string is a recognized boolean value or not
    """
    if value.lower() in ["true", "false", "t", "f", "yes", "no", "y", "n", "1", "0"]:
        return True
    else:
        return False


def convert_string_to_boolean(value: str) -> bool:
    """
    Converts a string to a boolean
    :param value: the string to be converted
    :return: the boolean value
    """
    if value.lower() in ["true", "t", "yes", "y", "1"]:
        return True
    elif value.lower() in ["false", "f", "no", "n", "0"]:
        return False
    else:
        raise ValueError("String is not a recognized boolean value")


def parse_filename(filename) -> (float, str, str, str):
    """
    INTERNAL USE ONLY
    :param filename: the filename to be parsed
    :return: a tuple containing the parsed filename components
    """
    # Regex to match the filename components
    match = re.match(r'(\d+)?([a-zA-Z])? (.*)\.(.*)', filename)
    if match:
        number = int(match.group(1)) if match.group(1) else float('inf')  # Use infinity for missing numbers
        letter = match.group(2) if match.group(2) else ''
        name = match.group(3)
        extension = match.group(4)
        return number, letter, name, extension
    else:
        # Handle files that don't match the expected pattern
        return float('inf'), '', filename, ''


def sort_list_by_numbering_system(str_list: list, return_only_filenames: bool = False, add_tab: bool = False) -> list:
    """
    Sorts a list of filenames by a numbering system
    :param str_list: the list of filenames to be sorted
    :param return_only_filenames: whether to return only the filenames or the full paths
    :param add_tab: whether to add a tab between the name and the extension
    :return: the sorted list of filenames
    """
    dirnames = [os.path.dirname(file) for file in str_list]
    filenames = [os.path.basename(file) for file in str_list]
    parsed_files = [parse_filename(file) for file in filenames]
    sorted_files = sorted(parsed_files, key=lambda x: (x[0], x[1], x[2]))

    recomposed_files = [
        ''.join([f"{x[0]}" if x[0] != float('inf') else '', x[1], f" {'\t' if add_tab else ''}{x[2]}.{x[3]}"]).strip()
        for x in sorted_files]
    recomposed_directories = [f"{dirnames[i]}/{recomposed_files[i]}" for i in range(len(recomposed_files))]
    return recomposed_files if return_only_filenames else recomposed_directories

def convert_float_to_string(number: float, length: int = -1) -> str:
    int_part = floor(number)
    len_int = len(str(int_part))
    str_float = str(number)
    for i in range(length - len_int):
        str_float = "0" + str_float

    return str_float

