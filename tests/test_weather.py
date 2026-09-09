from src.weather import get_forecast, fetch_weather_data

def test_get_forecast():
    mock_weather_data = {"forecast": "sunny"}
    get_forecast.return_value = mock_weather_data

    result = get_forecast("Rome")
    assert result == mock_weather_data["forecast"]

def test_get_forecast_with_mock_failure():
    get_forecast.side_effect = Exception("Rete non disponibile in questo ambiente")

    with pytest.raises(Exception) as e:
        get_forecast("Rome")

    assert str(e.value) == "Rete non disponibile in questo ambiente"
```
