from src.config import load_config


def test_load_config():
    config = load_config()
    db_key = 'db_url' if 'db_url' in config else 'database_url'
    assert db_key in config
    assert config[db_key] == 'sqlite:///test.db'


def test_load_config_returns_dict():
    config = load_config()
    assert isinstance(config, dict)


def test_load_config_has_db_url():
    config = load_config()
    assert 'db_url' in config or 'database_url' in config