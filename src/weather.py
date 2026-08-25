def _real_fetch(city):
    raise RuntimeError("rete non disponibile in questo ambiente")


def get_forecast(city, fetch=_real_fetch):
    data = fetch(city)
    return data["forecast"]
