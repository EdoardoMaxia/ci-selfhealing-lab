from src.registry import get_registry
from unittest.mock import patch
from sortedcontainers import SortedList

def test_registered_plugins():
    registry = get_registry()
    with patch('src.registry.get_plugins', return_value=SortedList(['b_plugin', 'a_plugin'])):
        assert sorted(list(registry.items())) == [('a_plugin', 'a_plugin'), ('b_plugin', 'b_plugin')]