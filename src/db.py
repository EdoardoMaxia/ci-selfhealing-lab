class Database:
    """Fake in-memory database (for test_012, no external dependency)."""

    def __init__(self):
        self._last = None

    def save(self, record, commit=True):
        self._last = record
        return True
