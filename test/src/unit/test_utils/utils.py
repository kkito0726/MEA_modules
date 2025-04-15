import math


def truncate(x: float, digits: int) -> float:
    factor = 10.0**digits
    return math.floor(x * factor) / factor
