import pytest
from src.calculator import power


def test_power():
    assert power(2, 3) == 8


def test_sum_floats():
    result = 0.1 + 0.2
    assert result == pytest.approx(0.3)


def square(n):
    return n * n


@pytest.mark.parametrize('n,expected', [(2,4),(3,9),(4,16)])
def test_square(n, expected):
    assert square(n) == expected