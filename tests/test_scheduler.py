from datetime import datetime, timezone
from src.scheduler import format_local
import pytest

def test_format_local_time():
    dt = datetime(2024, 1, 1, 14, 30, tzinfo=timezone.utc)
    # The test should account for the local timezone of the runner
    # Since GitHub Actions runners default to UTC, we expect '14:30 UTC'
    assert format_local(dt) == '14:30 UTC'