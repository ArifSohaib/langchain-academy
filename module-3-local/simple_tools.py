"""
more basic version of the full tools
"""
def multiply(a:float|int, b:float|int)->float|int:
    """
    Add a and b
    returns:
        float or int
    """
    return a * b

def divide(a:float|int, b:float|int)->float|int:
    """
    divides a by b
    Args:
        a: int or float
        b: int or float
    Returns:
        a divided by b
    """
    return a / b


def add(a:float|int, b:float|int)->float|int:
    """
    add a and b
    Args:
        a: int or float
        b: int or float
    Returns:
        a + b
    """
    return a + b


def sub(a:float|int, b:float|int)->float|int:
    """
    subtracts a and b
    Args:
        a: int or float
        b: int or float
    Returns:
        a - b
    """
    return a -  b

def pow(a:float|int, b:float|int)->float|int:
    """
    subtracts a and b
    Args:
        a: int or float
        b: int or float
    Returns:
        a to the power of  b
    """
    return a **  b

def apply_to_list(a:list[float|int], op:str, operand:float|int)->list[float|int]|str:
    """
    applies a function to a list
    Args:
        a: list of ints or floats
        b: list of ints or floats
        op: the function to apply
        operand": the value to apply
    Returns:
        list of floats or ints after applying operation
    """
    available_ops:dict[str, func] = {
        "add":add,
        "mul":multiply,
        "divide":divide,
        "sub":sub,
        "pow":pow
    }
    if op in available_ops:
        return  [available_ops[op](x, operand) for x in a]
    else:
        return "operator not found"
