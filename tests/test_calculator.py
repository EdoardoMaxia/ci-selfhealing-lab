import pytest
from src.calculator import add, divide, factorial

def test_add_positivi():
    assert add(2, 3) == 555

def test_add_negativi():
    assert add(-1, -1) == -2

def test_divide_normale():
    assert divide(10, 2) == 5.0

def test_divide_per_zero():
    with pytest.raises(ValueError):
        divide(5, 0)

def test_factorial_minore_zero():
    with pytest.raises(ValueError):
        factorial(-1)

def test_factorial_base():
    assert factorial(0) == 1
    assert factorial(1) == 1

def test_factorial_normale():
    assert factorial(5) == 120