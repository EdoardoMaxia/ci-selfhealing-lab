from src.utils import to_upper

def test_string_upper():
    assert to_upper('hello') == 'HELLO'

def test_string_upper_uppercase():
    assert to_upper('hello') == 'HELLO'