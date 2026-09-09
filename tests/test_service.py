from src.services import UserService


def test_fetch_user():
    service = UserService()
    user = service.fetch_user(1)
    assert user["name"] == "alice"