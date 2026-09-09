import pytest
from src.parser import parse


def test_invalid_input():
    with pytest.raises(TypeError, match="Invalid input"):
        parse(None)


def test_invalid_input_bool():
    with pytest.raises(TypeError, match="Invalid input"):
        parse(True)


def test_invalid_input_list():
    with pytest.raises(TypeError, match="Invalid input"):
        parse([1, 2, 3])