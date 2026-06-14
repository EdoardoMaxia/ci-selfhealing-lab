def test_user_creation():
    """Test creazione utente."""
    user = User(name='John') #type: ignore
    assert user.name == 'john'