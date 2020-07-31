from typing import List


def foo():
    return tuple((0. for _ in range(2)))


a, b = foo()