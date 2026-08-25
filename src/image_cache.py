class ImageCache:
    def __init__(self):
        self._store = {}

    def load(self, name):
        self._store[name] = f"<pixels:{name}>"
        return self._store[name]

    def clear(self):
        self._store.clear()

    def size(self):
        return len(self._store)
