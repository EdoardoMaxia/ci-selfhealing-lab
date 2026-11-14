class AuthConfig:
    MIN_PASSWORD_LENGTH = 8


class LoginResponse:
    def __init__(self, ok):
        self.ok = ok


def login(username, password):
    """Minimal login: rejects passwords shorter than the configured minimum."""
    if len(password) < AuthConfig.MIN_PASSWORD_LENGTH:
        return LoginResponse(ok=False)
    return LoginResponse(ok=True)
