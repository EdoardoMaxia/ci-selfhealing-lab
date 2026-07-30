class AuthConfig:
    MIN_PASSWORD_LENGTH = 8


class LoginResponse:
    def __init__(self, ok):
        self.ok = ok


def login(username, password):
    """Login minimale: rifiuta password piu' corte del minimo configurato."""
    if len(password) < AuthConfig.MIN_PASSWORD_LENGTH:
        return LoginResponse(ok=False)
    return LoginResponse(ok=True)
