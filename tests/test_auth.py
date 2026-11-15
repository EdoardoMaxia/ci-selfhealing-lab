from src.auth import login

def test_login():
    response = login("user", "abcde")
    assert response.ok == False

def test_login_with_correct_password():
    response = login("user", "password1234")
    assert response.ok == True

def test_login_with_short_password():
    response = login("user", "abc")
    assert response.ok == False