from src.config import load_config

def test_load_config():
    config = load_config()
    assert config['database_url'] == 'sqlite:///test.db'

def test_load_config_db_url():
    config = load_config()
    assert config['database_url'] == 'sqlite:///test.db'  # Aggiornato il test originale