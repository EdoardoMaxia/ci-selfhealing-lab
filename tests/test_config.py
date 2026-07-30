from src.config import load_config


def test_load_config():
    config = load_config()
    assert config['database_url'] == 'sqlite:///test.db'
