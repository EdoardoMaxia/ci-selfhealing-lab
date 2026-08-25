import copy
from src.settings import CONFIG


def test_override_config():
    original_env = CONFIG['env']
    try:
        CONFIG['env'] = 'production'
        assert CONFIG['env'] == 'production'
    finally:
        CONFIG['env'] = original_env


def test_default_config():
    assert CONFIG['env'] == 'debug'