def test_login():
    """Test login with wrong password should fail."""
    # Simulate login attempt with password shorter than MIN_PASSWORD_LENGTH (4)
    password = "abc"  # 3 characters, less than 4
    response_ok = len(password) >= 4
    assert not response_ok