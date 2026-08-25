class TTLCache:
    """Cache con scadenza (TTL) basata su un clock iniettabile, per test deterministici."""

    def __init__(self, ttl_seconds, clock=None):
        self._ttl = ttl_seconds
        self._clock = clock or (lambda: 0)
        self._store = {}

    def set(self, key, value):
        self._store[key] = (value, self._clock())

    def get(self, key):
        if key not in self._store:
            return None
        value, ts = self._store[key]
        if self._clock() - ts >= self._ttl:
            del self._store[key]
            return None
        return value
