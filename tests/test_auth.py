from src.auth import login


def test_login():
    # 5 characters: rejected with minimum 8, (wrongly) accepted with minimum 4
    response = login("user", "abcde")
    assert response.ok == False
