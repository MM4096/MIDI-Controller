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
    try:
        int(value)
        return True
    except ValueError:
        return False
