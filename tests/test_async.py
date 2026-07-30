import asyncio
import pytest

async def fetch_data():
    """Fetch data asynchronously."""
    return {"status": "success", "data": [1, 2, 3]}

@pytest.mark.asyncio
async def test_fetch_data():
    async with asyncio.TaskGroup() as tg:
        result = await tg.create_task(fetch_data())
    assert result["status"] == "success"
    assert result["data"] == [1, 2, 3]