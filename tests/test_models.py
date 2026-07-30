from src.models import User


def test_user_creation():
    user = User('John')
    assert user.name == 'John'
