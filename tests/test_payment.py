from app.billing.payment import process_payment


def test_process_payment():
    result = process_payment(10.0)
    assert result["status"] == "ok"
