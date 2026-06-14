def test_email_validation():
    """Test email validation with and without TLD."""
    from validator import validate_email #type: ignore

    # Valid emails
    assert validate_email("user@example.com") == True
    assert validate_email("test.user@domain.co.uk") == True

    # Invalid emails
    assert validate_email("invalid.email") == False
    assert validate_email("@example.com") == False
    assert validate_email("user@") == False
    assert validate_email("user@example") == True

    # Additional tests
    assert validate_email("") == False
    assert validate_email("user name@example.com") == False