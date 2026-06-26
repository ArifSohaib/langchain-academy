"""## Tools used in other files"""

from functools import reduce
from typing import List


def multiply(a: int | float, b: int | float) -> int | float:
    return a * b


def divide(a: int | float, b: int | float) -> int | float:
    if b != 0:
        return a / b
    else:
        raise ValueError("not divisable by b == 0")


def add(a: int | float, b: int | float) -> int | float:
    return a + b


def sub(a: int | float, b: int | float) -> int | float:
    return a - b


def pow(a: int | float, b: int | float) -> int | float:
    return a**b


def split_string(a: str) -> list:
    return [char for char in a]


def equals(a: str | float | int, b: str | float | int) -> bool:
    if type(a) is not type(b):
        return False
    return a == b


def convert_str_to_int(a: str) -> List[int]:
    return [ord(x) for x in a]


def greater_than(a: float | int, b: float | int) -> bool:
    if type(a) is not type(b):
        return False
    return a > b


def less_than(a: float | int, b: float | int) -> bool:
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
    "convert_str_to_int": convert_str_to_int,
    "less_than": less_than,
}


def apply_over_list(
    op_name: str, lst: List[int | float], operand: int | float
) -> List[int | float]:
    """
    Apply a two argument scalar scalar operation to every element of a list
    """
    if op_name not in _SCALAR_OPS:
        raise ValueError(f"unknown operation {op_name}; choose from {_SCALAR_OPS}")
    func = _SCALAR_OPS[op_name]
    return [func(x, operand) for x in lst]


def reduce_over_list(
    op_name: str,
    lst: List[int | float],
) -> int | float:
    """
    Apply a two argument scalar operation to a list and reduce the result
    """
    if op_name not in _SCALAR_OPS:
        raise ValueError(f"unknown operation {op_name} choose from {_SCALAR_OPS}")
    func = _SCALAR_OPS[op_name]
    return reduce(lambda acc, x: func(acc, x), lst)


def remove_from_end_of_list(lst: List) -> Tuple[List, str | int | float]:
    item = lst.pop()
    return lst, item


def remove_from_list(lst: List, item: str | int | float):
    try:
        idx = lst.index(item)
        del lst[idx]
    except ValueError:
        print(f"item {item} not present")
    return lst
