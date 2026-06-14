import pytest
from service import UserService #type: ignore


class TestUserService:
    def setup_method(self):
        self.service = UserService()
    
    def test_fetch_user(self):
        """Test that fetch_user returns user data correctly."""
        user = self.service.fetch_user(1)
        assert user is not None
        assert user['id'] == 1
    
    def test_fetch_user_not_found(self):
        """Test that fetch_user raises error for non-existent user."""
        with pytest.raises(ValueError):
            self.service.fetch_user(999)

    def test_get_user(self): # Aggiungo un nuovo test per il metodo get_user
        """Test che get_user restituisca i dati utente correttamente."""
        user = self.service.get_user(1)
        assert user is not None
        assert user['id'] == 1

    def test_get_user_not_found(self): # Aggiungo un nuovo test per il metodo get_user
        """Test che get_user sollevi errore per utente non esistente."""
        with pytest.raises(ValueError):
            self.service.get_user(999)