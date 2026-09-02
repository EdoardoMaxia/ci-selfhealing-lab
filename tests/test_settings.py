import copy
from src.settings import CONFIG


def test_override_config():
    original_config = copy.deepcopy(CONFIG)
    CONFIG['env'] = 'production'
    assert CONFIG['env'] == 'production'
    CONFIG.update(original_config)


def test_default_config():
    assert CONFIG['env'] == 'debug'