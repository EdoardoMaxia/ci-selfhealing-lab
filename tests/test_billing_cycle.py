import pytest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def test_hours_between():
    tz = ZoneInfo("Europe/Rome")
    # Explicit conversion to UTC before subtracting: if two datetimes with
    # the same tzinfo are subtracted directly, Python ignores the offset
    # and compares the "naive" times, hiding the daylight saving time jump.
    start = datetime(2024, 3, 31, 0, 0, tzinfo=tz).astimezone(timezone.utc)
    end = datetime(2024, 4, 1, 0, 0, tzinfo=tz).astimezone(timezone.utc)
    delta = end - start
    assert delta.total_seconds() / 3600 == 24
