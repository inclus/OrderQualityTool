def as_float_or_1(value):
    try:
        return float(value)
    except ValueError as e:
        return 1
    except TypeError as e:
        return 1


def as_number(value):
    if value is None:
        return False, value
    try:
        return True, float(value)
    except ValueError as e:
        print(e, "--")
        return False, None
