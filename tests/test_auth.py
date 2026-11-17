from src.auth import login

def test_login():
    response = login("user", "abcde")
    assert response.ok is False