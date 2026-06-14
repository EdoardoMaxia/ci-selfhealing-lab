import asyncio
import pytest

async def fetch_data():
    """Fetch data asynchronously."""
    return {"status": "success", "data": [1, 2, 3]}

def setup():
    """Setup function."""
    pass

@pytest.mark.asyncio
async def test_fetch_data():
    result = await fetch_data()
    assert result["status"] == "success"
    assert result["data"] == [1, 2, 3]