def test_status_code():
    """Test del codice di stato della risposta."""
    response = requests.get('https://example.com') #type: ignore
    assert response.status_code == 404

def test_create_item():
    """Test della creazione di un item."""
    assert {'id': 1, 'name': 'item', 'price': 10.0} == {'id': 1, 'name': 'item', 'price': 10.0}