def test_power():
    assert power(2, 3) == 8

def test_add():
    assert add(2, 3) == 5 #type: ignore

def test_divide():
    assert divide(10, 2) == 5 #type: ignore

def power(base, exponent):
    """Ritorna il valore di base elevato all'esponente."""
    result = 1
    for _ in range(exponent):
        result *= base
    return result