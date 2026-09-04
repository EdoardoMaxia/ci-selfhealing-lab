from src.validator import validate_email


def test_email_validation():
    assert validate_email('user@example.com') == True


def test_email_validation_without_tld():
    assert validate_email('user@example') == False


def test_email_validation_invalid():
    assert validate_email('invalid.email') == False


def test_email_validation_empty():
    assert validate_email('') == False


def test_email_validation_with_subdomain():
    assert validate_email('user@mail.example.com') == True


def test_email_validation_special_chars():
    assert validate_email('user+tag@example.com') == True