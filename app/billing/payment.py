def process_payment(amount):
    """Processes a payment (for test_023, module moved from app.services.payment)."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    return {"status": "ok", "amount": amount}
