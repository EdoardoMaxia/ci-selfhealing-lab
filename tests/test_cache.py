from src.cache import TTLCache

def test_cache_invalidation():
    fake_time = [0]
    cache = TTLCache(ttl_seconds=300, clock=lambda: fake_time[0])

    cache.set("key", "old_value")
    fake_time[0] = 301
    assert cache.get("key") is None

    fake_time[0] = 0
    cache.set("key", "new_value")
    assert cache.get("key") == "new_value"
