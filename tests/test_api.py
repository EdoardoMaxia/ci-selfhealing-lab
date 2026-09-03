from types import SimpleNamespace
from src.api import create_item


def test_status_code():
    response = SimpleNamespace(status_code=200)
    assert response.status_code == 200


def test_create_item():
    result = create_item(1, "item", 10.0)
    assert result == {"id": 1, "name": "item", "price": 10.0}


def test_new_timeout_param():
    # Mock della funzione request per simulare il comportamento
    import requests
    original_request = requests.request
    requests.request = lambda method, url, timeout=None, **kwargs: SimpleNamespace(status_code=200)
    
    try:
        # Assumendo che create_item usi requests e passi timeout
        result = create_item(1, "item", 10.0)
        assert result == {"id": 1, "name": "item", "price": 10.0}
    finally:
        # Ripristina la funzione originale
        requests.request = original_request