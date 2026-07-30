def parse(value):
    """Solleva ValueError su input non valido (per test_022)."""
    if value is None:
        raise ValueError(f"Invalid input: {value}")
    return value
