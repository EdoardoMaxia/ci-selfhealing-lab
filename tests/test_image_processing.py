from src.image_cache import ImageCache


def test_resize_iterations():
    cache = ImageCache()
    for name in ["a", "b", "c"]:
        cache.load(name)
        pass  # clear() removed by mistake
    assert cache.size() == 0
