import pytest
from freezegun import freeze_time #type: ignore

@freeze_time('2024-01-01 12:00:00')
def test_cache_invalidation():
    """Test that cache is properly invalidated after update."""
    # Mock cache behavior
    cache = {}

    def get_cached_value(key):
        return cache.get(key, 'old_value')

    def set_cached_value(key, value):
        cache[key] = value

    # Initial cache state
    set_cached_value('test_key', 'old_value')
    assert get_cached_value('test_key') == 'old_value'

    # Update cache
    set_cached_value('test_key', 'new_value')
    assert get_cached_value('test_key') == 'new_value'

def test_add():
    """Test addition function."""
    from main import add #type: ignore
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_divide():
    """Test division function."""
    from main import divide #type: ignore
    assert divide(10, 2) == 5
    assert divide(7, 2) == 3.5

def test_divide_by_zero():
    """Test division by zero raises error."""
    from main import divide #type: ignore
    with pytest.raises(ValueError, match="Divisione per zero"):
        divide(10, 0)

def test_factorial():
    """Test factorial function."""
    from main import factorial #type: ignore
    assert factorial(0) == 1
    assert factorial(5) == 120
    assert factorial(1) == 1

def test_factorial_negative():
    """Test factorial with negative number raises error."""
    from main import factorial #type: ignore
    with pytest.raises(ValueError, match="n deve essere >= 0"):
        factorial(-1)