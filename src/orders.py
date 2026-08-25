def create_order(session, item_id):
    """Crea un ordine minimale nella sessione fornita (per test_024/test_038)."""
    order = {
        "id": len(session.setdefault("orders", [])) + 1,
        "item_id": item_id,
        "status": "pending",
    }
    session["orders"].append(order)
    return order
