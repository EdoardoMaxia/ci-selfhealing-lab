from src.auth import login


def test_login():
    # 5 caratteri: rifiutata col minimo a 8, accettata (erroneamente) col minimo a 4
    response = login("user", "abcde")
    assert response.ok == False
