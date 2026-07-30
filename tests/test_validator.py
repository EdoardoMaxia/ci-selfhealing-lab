from src.validator import validate_email


def test_email_validation():
    assert validate_email('user@example') == False
