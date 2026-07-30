class UserService:
    """Servizio utenti minimale, in-memory (per test_009)."""

    def __init__(self):
        self._users = {1: {"id": 1, "name": "alice"}}

    def get_user(self, user_id):
        return self._users.get(user_id)
