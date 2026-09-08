from src.auth import login


def test_login():
    # 3 caratteri: rifiutata col minimo a 4
    response = login("user", "abc")
    assert response.ok == False