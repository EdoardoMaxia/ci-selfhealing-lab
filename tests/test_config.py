from src.config import load_config


def test_load_config():
    config = load_config()
    assert isinstance(config, dict)
    assert 'db_url' in config or 'database_url' in config
    db_url = config.get('db_url') or config.get('database_url')
    assert db_url == 'sqlite:///test.db'