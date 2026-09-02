import asyncio
from src.fetcher import fetch_data


def test_fetch_data():
    async def runner():
        return await fetch_data()

    result = asyncio.run(runner())
    assert result["status"] == "success"
    assert result["data"] == [1, 2, 3]