from src.image_cache import ImageCache

def test_resize_iterations():
    cache = ImageCache()
    for name in ["a", "b", "c"]:
        cache.load(name)
        cache.clear()
    assert cache.size() == 0