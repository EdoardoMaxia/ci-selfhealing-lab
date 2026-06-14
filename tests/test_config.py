import pytest
from config import load_config #type: ignore

def test_load_config():
    config = load_config() #type: ignore
    assert config['db_url'] == 'sqlite:///test.db'

def test_add():
    from main import add #type: ignore
    assert add(2, 3) == 5

def test_divide():
    from main import divide #type: ignore
    with pytest.raises(ValueError):
        divide(10, 0)
    assert divide(10, 2) == 5

def test_factorial():
    from main import factorial #type: ignore
    assert factorial(5) == 120

def test_load_config_correct_key():
    config = load_config()
    assert config['db_url'] == 'sqlite:///test.db'

def test_config_file():
    from config import Config #type: ignore
    with pytest.raises(KeyError):
        Config({})
    with open('config.ini', 'r') as f:
        data = f.read()
        assert 'db_url' in data