def process_payment(amount):
    """Elabora un pagamento (per test_023, modulo spostato da app.services.payment)."""
    if amount <= 0:
        raise ValueError("amount deve essere positivo")
    return {"status": "ok", "amount": amount}
