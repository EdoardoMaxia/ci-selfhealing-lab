_store = {}


def increment_counter(key, amount=1):
    _store[key] = _store.get(key, 0) + amount
    return _store[key]


def reset():
    _store.clear()


def make_key(namespace):
    return f"counter:{namespace}"
