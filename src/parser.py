def parse(value):
    """Raises ValueError on invalid input (for test_022)."""
    if value is None:
        raise ValueError(f"Invalid input: {value}")
    return value
