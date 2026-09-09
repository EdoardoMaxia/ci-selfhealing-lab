import os
import pytest

def test_acquire_lock():
    lock_file = '/tmp/app.lock'
    
    # Assicurati che il file di lock non esista prima del test
    if os.path.exists(lock_file):
        os.remove(lock_file)
    
    # Simula l'acquisizione del lock
    try:
        with open(lock_file, 'x') as f:
            f.write('locked')
    except FileExistsError:
        pytest.fail("Lock file already exists, test setup failed.")
    
    # Verifica che il file di lock esista dopo l'acquisizione
    assert os.path.exists(lock_file)
    
    # Pulisci il file di lock dopo il test
    os.remove(lock_file)