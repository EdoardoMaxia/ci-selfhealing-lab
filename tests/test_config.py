from src.config import load_config


def test_load_config():
    config = load_config()
    assert isinstance(config, dict)
    db_value = config.get('db_url') or config.get('database_url')
    assert db_value == 'sqlite:///test.db'


def test_load_config_returns_dict():
    config = load_config()
    assert isinstance(config, dict)


def test_load_config_has_db_key():
    config = load_config()
    assert 'db_url' in config or 'database_url' in config