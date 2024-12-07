import math

PRECISION = 10

def calculate_cos(arg):
    """
    Calculate cosine value up to the precision.
    """
    cos = math.cos(math.pi*arg)
    return round(cos, PRECISION)

def is_equal_float_num(lhs, rhs):
    """
    Check two numbers are equal up to the precision.
    """
    return round(lhs, PRECISION) == round(rhs, PRECISION)

def compare_float_num(lhs, rhs):
    """
    Compare two numbers upt to the precision.

    Return:
        True: if the first arg is larger than the second one
        False: if the first arg is smaller or equal to the second one
    """
    return round(lhs, PRECISION) > round(rhs, PRECISION)

def is_integer(value):
    """
    Check the number is an integer.
    """
    rounded_value = round(value, PRECISION)
    return rounded_value.is_integer()