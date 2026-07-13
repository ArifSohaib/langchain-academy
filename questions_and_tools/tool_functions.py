"""## Tools used in other files"""

from functools import reduce
from typing import List, Tuple

from typing_extensions import Callable


def multiply(a: int | float, b: int | float) -> int | float:
    """
    multiply two numbers and return the result
    Args:
        a: int|float first number
        b:int:float second number
    Returns:
        int|float mult result
    """
    return a * b


def divide(a: int | float, b: int | float) -> int | float:
    """
    divide two numbers and return the result
    Args:
        a: int|float first number
        b:int:float second number
    Returns:
        int|float mult result
    """
    if b != 0:
        return a / b
    else:
        raise ValueError("not divisable by b == 0")


def add(a: int | float, b: int | float) -> int | float:
    """
    add two numbers and return the result
    Args:
        a: int|float first number
        b:int:float second number
    Returns:
        int|float mult result
    """
    return a + b


def sub(a: int | float, b: int | float) -> int | float:
    """
    subtract two numbers and return the result
    Args:
        a: int|float first number
        b:int:float second number
    Returns:
        int|float mult result
    """
    return a - b


def pow(a: int | float, b: int | float) -> int | float:
    """
    exponent of a given number to a second number and return the result
    Args:
        a: int|float first number
        b:int:float second number
    Returns:
        int|float mult result
    """
    return a**b


def split_string(a: str) -> list[str]:
    """
    given a string return the result as list of chars
    Args:
        a: str : string to split
    Returns:
        list of chars
    """
    return [char for char in a]


def equals(a: str | float | int, b: str | float | int) -> bool:
    """
    equality operator
    Args:
        a : number to compare
        b : second number to compare
    Returns:
        boolian indicating if the two values are the same
    """
    if type(a) is not type(b):
        return False
    return a == b


def convert_str_to_int(a: str) -> List[int]:
    """
    given a string convert each character into an integer and return the result
    Args:
        a: string to split and convert to int

    """
    return [ord(x) for x in a]


def greater_than(a: float | int, b: float | int) -> bool:
    """
    given a number compare it to second number and return if first number is larger than the second number
    """
    if type(a) is not type(b):
        return False
    return a > b


def less_than(a: float | int, b: float | int) -> bool:
    """
    given a number compare it to a second number and return true if first number is lower than second
    """
    if type(a) is not type(b):
        return False
    return a < b


_SCALAR_OPS = {
    "multiply": multiply,
    "divide": divide,
    "add": add,
    "sub": sub,
    "power": pow,
    "equals": equals,
    "greater_than": greater_than,
    "less_than": less_than,
}


def apply_over_list(
    op_name: str, lst: List[int | float], operand: int | float
) -> List[int | float]:
    """
    Apply a two argument scalar scalar operation to every element of a list
    Args:
        op_name: the operation to apply from _SCALAR_OPS
        lst: list to apply the operation to
        operand: value to use for operation eg for adding a provided number to all values to a list, operand would be the number to add
    Returns:
        list with operation applied
    """
    if op_name not in _SCALAR_OPS:
        raise ValueError(f"unknown operation {op_name}; choose from {_SCALAR_OPS}")
    func = _SCALAR_OPS[op_name]
    return [func(x, operand) for x in lst]


def reduce_over_list(op_name: str, lst: List[int | float]) -> int | float:
    """
    Apply a two argument scalar operation to a list and reduce the result
    Args:
        op_name: the operation to apply from _SCALAR_OPS
        lst: list to apply the operation to
    Returns:
        value after reducing list using operation
    """
    if op_name not in _SCALAR_OPS:
        raise ValueError(f"unknown operation {op_name} choose from {_SCALAR_OPS}")
    func = _SCALAR_OPS[op_name]
    return reduce(lambda acc, x: func(acc, x), lst)


def remove_from_end_of_list(lst: List) -> Tuple[List, str | int | float]:
    """
    remove a value from the end of the list
    Args:
        lst:List list to remove item from
    Returns:
        lst: List[str|innt|float]  the remaining list
        item: str|int|float the value of the list item
    """
    item = lst.pop()
    return lst, item


def remove_first_n(lst: List[int | float], n: int) -> List[int | float]:
    """
    Removes first n values from list
    Args:
        lst: list to remove items from
        n: number of items to remove
    Returns:
        list after removing items
    """
    return lst[n:]


def remove_last_n(lst: List[int | float], n: int) -> List[int | float]:
    """
    remove last n values from list
    Args:
        lst: list to remove items from
        n: number of items to remove
    Returns:
        list after removing items
    """
    return lst[:n]


def add_lists(lst1: List[int | float], lst2: List[int | float]) -> List[int | float]:
    """
    append list to another list
    Args:
        lst1: list to append to (first numbers)
        lst2: list to add (last numbers)
    """
    return lst1 + lst2


def remove_from_list(lst: List, item: str | int | float) -> List[str | int | float]:
    """
    remove first instance of a provided value from the list
    Args:
        lst: List to remove item from
        item: the item to remove
    Returns:
        lst: List[str|innt|float]  the remaining list
    """
    try:
        idx = lst.index(item)
        del lst[idx]
    except ValueError:
        print(f"item {item} not present")
    return lst


def sum_over_list(list: List[int | float]) -> int | float:
    """
    return sum of a list
    Args:
        list: the list to sum
    """
    return sum(list)


_TOOLS: dict[str, Callable] = {
    "apply_over_list": apply_over_list,
    "reduce_over_list": reduce_over_list,
    "multiply": multiply,
    "divide": divide,
    "add": add,
    "sub": sub,
    "pow": pow,
    "split_string": split_string,
    "convert_str_to_int": convert_str_to_int,
    "convert_equals": equals,
    "greater_than": greater_than,
    "less_than": less_than,
    "remove_from_end_of_list": remove_from_end_of_list,
    "remove_from_list": remove_from_list,
    "add_lists": add_lists,
    "remove_last_n": remove_last_n,
    "remove_first_n": remove_first_n,
}
tool_list = list(_TOOLS.values())
