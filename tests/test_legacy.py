import pytest
from src.legacy import normalize


def test_old_behavior():
    assert normalize('  Hello  ') == 'hello'
