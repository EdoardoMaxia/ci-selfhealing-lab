def _real_fetch(city):
    raise RuntimeError("network not available in this environment")


def get_forecast(city, fetch=_real_fetch):
    data = fetch(city)
    return data["forecast"]
