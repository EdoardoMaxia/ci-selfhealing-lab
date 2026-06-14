def test_string_upper():
    assert to_upper('hello') == 'HELLO'.upper() == 'HELLO'

def test_add():
    assert add(2, 3) == 5 #type: ignore

def test_divide():
    assert divide(10, 2) == 5 #type: ignore

def test_factorial():
    assert factorial(5) == 120 #type: ignore

def to_upper(s):
    """Converte una stringa in maiuscolo."""
    return s.upper()