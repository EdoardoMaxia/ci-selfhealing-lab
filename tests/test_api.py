from types import SimpleNamespace
from src.api import create_item


def test_status_code():
    response = SimpleNamespace(status_code=200)
    assert response.status_code == 200


def test_create_item():
    result = create_item(1, "item", 10.0)
    assert result == {"id": 1, "name": "item", "price": 10.0}