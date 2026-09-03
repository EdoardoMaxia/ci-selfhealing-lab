import pytest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def test_hours_between():
    tz = ZoneInfo("Europe/Rome")
    # Conversione esplicita a UTC prima della sottrazione: se si sottraggono
    # direttamente due datetime con lo stesso tzinfo, Python ignora l'offset
    # e confronta gli orari "naive", nascondendo il salto dell'ora legale.
    start = datetime(2024, 3, 31, 0, 0, tzinfo=tz).astimezone(timezone.utc)
    end = datetime(2024, 4, 1, 0, 0, tzinfo=tz).astimezone(timezone.utc)
    delta = end - start
    assert delta.total_seconds() / 3600 == pytest.approx(24, abs=1)