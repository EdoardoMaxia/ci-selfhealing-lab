import pytest
import os

def test_acquire_lock():
    lock_file = '/tmp/app.lock'
    try:
        with open(lock_file, 'w') as f:
            f.write('locked')
        assert os.path.exists(lock_file)
    finally:
        if os.path.exists(lock_file):
            os.remove(lock_file)