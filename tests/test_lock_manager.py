import os
import pytest

def test_acquire_lock():
    lock_file = '/tmp/app.lock'
    
    # Ensure the lock file does not exist before the test
    if os.path.exists(lock_file):
        os.remove(lock_file)
    
    # Simulate acquiring the lock
    try:
        with open(lock_file, 'x') as f:
            f.write('lock')
    except FileExistsError:
        pytest.fail("Lock file already exists, test setup failed.")
    
    # Clean up after test
    if os.path.exists(lock_file):
        os.remove(lock_file)