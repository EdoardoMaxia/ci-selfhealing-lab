import asyncio


async def fetch_data():
    """Recupera dati in modo asincrono (nessuna I/O reale, solo un giro di event loop)."""
    await asyncio.sleep(0)
    return {"status": "success", "data": [1, 2, 3]}
