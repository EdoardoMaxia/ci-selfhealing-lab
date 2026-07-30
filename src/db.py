class Database:
    """Database fittizio in-memory (per test_012, nessuna dipendenza esterna)."""

    def __init__(self):
        self._last = None

    def save(self, record, commit=True):
        self._last = record
        return True
