from src.config import load_config


def test_load_config():
    config = load_config()
    assert config['db_url'] == 'sqlite:///test.db'