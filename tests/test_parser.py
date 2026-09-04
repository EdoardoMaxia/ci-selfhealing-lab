import pytest
from src.parser import parse


def test_invalid_input():
    with pytest.raises(TypeError):
        parse(None)