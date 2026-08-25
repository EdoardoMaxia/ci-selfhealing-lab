from datetime import datetime, timezone, timedelta
from src.scheduler import format_local

def test_format_local_time():
    dt = datetime(2024, 1, 1, 14, 30, tzinfo=timezone.utc)
    # Adjust the expected time to match the UTC input
    assert format_local(dt) == '14:30 UTC'