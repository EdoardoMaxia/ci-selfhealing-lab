import asyncio
from src.fetcher import fetch_data


def test_fetch_data():
    result = asyncio.run(fetch_data())
    assert result["status"] == "success"
    assert result["data"] == [1, 2, 3]
