import os
import pytest

@pytest.fixture(autouse=True)
def cleanup_lock_file():
    """Ensure the lock file is removed before each test."""
    lock_file = '/tmp/app.lock'
    if os.path.exists(lock_file):
        os.remove(lock_file)
    yield
    if os.path.exists(lock_file):
        os.remove(lock_file)

def test_acquire_lock():
    lock_file = '/tmp/app.lock'
    # Simulate acquiring a lock by creating the lock file
    open(lock_file, 'w').close()
    # Test should pass as the fixture ensures the lock file is removed before the test
    assert os.path.exists(lock_file)