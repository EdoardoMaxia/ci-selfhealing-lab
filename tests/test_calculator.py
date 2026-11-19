import pytest
from src.calculator import add, divide, factorial

def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2

def test_divide_normal():
    assert divide(10, 2) == 5.0

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(5, 0)

def test_factorial_less_than_zero():
    with pytest.raises(ValueError):
        factorial(-1)

def test_factorial_base():
    assert factorial(0) == 1
    assert factorial(1) == 1

def test_factorial_normal():
    assert factorial(2) == 2
    assert factorial(3) == 6
    assert factorial(4) == 24
    assert factorial(5) == 120
    assert factorial(6) == 720