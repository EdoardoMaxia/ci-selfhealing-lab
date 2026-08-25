from src.weather import get_forecast


def fake_fetch(city):
    return {"forecast": "sunny"}


def test_get_forecast():
    result = get_forecast("Rome", fetch=fake_fetch)
    assert result == "sunny"
