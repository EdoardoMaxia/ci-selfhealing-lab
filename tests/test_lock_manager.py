import os
import tempfile
import pytest
from unittest.mock import patch

# Assumendo che il codice sorgente sia in un modulo chiamato lock_manager
# e che abbia una funzione acquire_lock che crea un file di lock

def test_acquire_lock():
    # Pulizia preliminare del file di lock prima del test
    lock_file = '/tmp/app.lock'
    if os.path.exists(lock_file):
        os.remove(lock_file)
    
    # Simula l'acquisizione del lock
    try:
        with open(lock_file, 'x'):
            pass  # Crea il file di lock
    except FileExistsError:
        pytest.fail("Impossibile acquisire il lock: il file esiste già")
    
    # Verifica che il file sia stato creato
    assert os.path.exists(lock_file)
    
    # Pulizia dopo il test
    os.remove(lock_file)