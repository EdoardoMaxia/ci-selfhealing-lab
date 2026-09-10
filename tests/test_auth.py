from src.auth import login

def test_login():
    # 8 caratteri: rifiutata col minimo a 8 (corretto)
    response = login("user", "abcde")
    assert response.ok == False

    # 8 caratteri: rifiutata col minimo a 8, accettata (erroneamente) col minimo a 4 (corretto)
    response = login("user", "abcdefgh")
    assert response.ok == True