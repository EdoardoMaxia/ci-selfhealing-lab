from src.services import UserService


def test_get_user():
    service = UserService()
    user = service.fetch_user(1)
    assert user["name"] == "alice"