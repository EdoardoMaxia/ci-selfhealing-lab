import os
import tempfile
import pytest
from unittest.mock import patch

# Assumendo che il codice sorgente sia in un modulo chiamato lock_manager
# e che abbia una funzione acquire_lock che crea un file di lock

def test_acquire_lock():
    # Pulizia preliminare del file di lock se esiste
    lock_file = '/tmp/app.lock'
    if os.path.exists(lock_file):
        os.remove(lock_file)
    
    # Simula l'acquisizione del lock
    try:
        with open(lock_file, 'x') as f:
            f.write("locked")
        assert True
    except FileExistsError:
        pytest.fail("Lock file already exists, indicating another process holds the lock")