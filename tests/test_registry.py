from src.registry import get_registry


def test_registered_plugins():
    registry = get_registry()
    assert sorted(registry.keys()) == ['a_plugin', 'b_plugin']
