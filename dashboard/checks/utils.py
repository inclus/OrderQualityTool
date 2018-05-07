def as_float_or_1(value, default=1):
    try:
        return float(value)
    except ValueError as e:
        return default
    except TypeError as e:
        return default


def as_number(value):
    if value is None:
        return False, value
    try:
        return True, float(value)
    except ValueError as e:
        return False, None
