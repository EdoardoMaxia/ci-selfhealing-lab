import copy
from src.settings import CONFIG


def test_override_config():
    config = copy.deepcopy(CONFIG)
    config['env'] = 'production'
    assert config['env'] == 'production'


def test_default_config():
    assert CONFIG['env'] == 'debug'