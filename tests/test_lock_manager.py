import os
import tempfile
import pytest
from unittest.mock import patch

def test_acquire_lock():
    # Ensure the lock file doesn't exist before the test
    lock_file = '/tmp/app.lock'
    
    # Clean up any existing lock file
    if os.path.exists(lock_file):
        os.remove(lock_file)
    
    # Test that the lock file is created successfully when it doesn't exist
    try:
        # This simulates the normal case where no lock exists
        with open(lock_file, 'x'):
            pass  # File created successfully
        os.remove(lock_file)  # Clean up
    except FileExistsError:
        pytest.fail("Failed to create lock file")
        
    # Test that acquiring an existing lock raises FileExistsError
    # First, create the lock file
    with open(lock_file, 'x'):
        pass  # File created successfully
    
    # Now try to acquire it again - should raise FileExistsError
    with pytest.raises(FileExistsError):
        with open(lock_file, 'x'):
            pass
            
    # Clean up
    os.remove(lock_file)