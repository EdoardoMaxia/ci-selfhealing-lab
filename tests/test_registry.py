from src.registry import get_registry


def test_registered_plugins():
    registry = get_registry()
    assert list(registry.keys()) == ['b_plugin', 'a_plugin']