from src.config import load_config

def test_load_config():
    config = load_config()
    assert config['database_url'] == 'sqlite:///test.db'

def test_load_config_with_default():
    config = load_config(default_database_url='sqlite:///test.db')
    assert config['database_url'] == 'sqlite:///test.db'

def test_load_config_with_wrong_url():
    with pytest.raises(KeyError):
        load_config(database_url='wrong_url')
```
