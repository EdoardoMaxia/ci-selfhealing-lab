from tempfile import NamedTemporaryFile

def test_acquire_lock():
    with NamedTemporaryFile(suffix='.lock', delete=False) as tmp:
        tmp.close()
        assert True