from src.services import UserService

def test_get_user():
    service = UserService()
    user = service.fetch_user(1)
    assert user["name"] == "alice"

def test_get_user_invalid_id():
    service = UserService()
    user = service.fetch_user(999)
    assert user is None

def test_get_user_invalid_id_type():
    service = UserService()
    user = service.fetch_user("abc")
    assert user is None