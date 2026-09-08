import os
import pytest

def test_acquire_lock():
    lock_file = '/tmp/app.lock'
    
    # Ensure the lock file is removed before the test
    if os.path.exists(lock_file):
        os.remove(lock_file)
    
    # Simulate acquiring a lock by creating the lock file
    open(lock_file, 'w').close()
    
    # Test that acquiring the lock again raises an error
    with pytest.raises(FileExistsError):
        open(lock_file, 'x')
    
    # Clean up after test
    os.remove(lock_file)