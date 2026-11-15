from src.auth import login

def test_login():
    # 5 characters: rejected with minimum 8, (wrongly) accepted with minimum 4
    response = login("user", "abcde")
    assert response.ok == False  # Corrected the assertion to reflect the expected behavior

    # Additional test to ensure the correct minimum password length is enforced
    response = login("user", "12345")
    assert response.ok == False

def test_login_min_password_length():
    # Test that login fails with password shorter than MIN_PASSWORD_LENGTH
    response = login("user", "1234")
    assert response.ok == False