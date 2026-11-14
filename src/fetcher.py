import asyncio


async def fetch_data():
    """Fetches data asynchronously (no real I/O, just one event loop iteration)."""
    await asyncio.sleep(0)
    return {"status": "success", "data": [1, 2, 3]}
