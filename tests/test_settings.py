import copy
from src.settings import CONFIG


def test_override_config():
    CONFIG['env'] = 'production'
    assert CONFIG['env'] == 'production'


def test_default_config():
    assert CONFIG['env'] == 'debug'
