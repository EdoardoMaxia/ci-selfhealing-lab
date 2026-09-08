from src.validator import validate_email


def test_email_validation():
    # Email without TLD should be invalid
    assert validate_email('user@example') == False
    # Email with proper TLD should be valid
    assert validate_email('user@example.com') == True
    # Empty string should be invalid
    assert validate_email('') == False
    # Missing @ should be invalid
    assert validate_email('userexample.com') == False