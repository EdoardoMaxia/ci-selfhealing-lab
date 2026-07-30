def test_string_upper():
    from utils import to_upper
    assert to_upper('hello') == 'hello'

def test_add():
    from utils import add
    assert add(2, 3) == 5

def test_divide():
    from utils import divide
    assert divide(10, 2) == 5

def test_factorial():
    from utils import factorial
    assert factorial(5) == 120