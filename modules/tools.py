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

