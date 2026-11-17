import pytest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def test_hours_between():
    tz = ZoneInfo("Europe/Rome")
    start = datetime(2024, 3, 31, 0, 0, tzinfo=tz).astimezone(timezone.utc)
    end = datetime(2024, 4, 1, 0, 0, tzinfo=tz).astimezone(timezone.utc)
    delta = end - start
    assert delta.total_seconds() / 3600 == pytest.approx(24, abs=1)