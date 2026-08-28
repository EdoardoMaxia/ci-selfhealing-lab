from datetime import datetime, timezone
from src.scheduler import format_local


def test_format_local_time():
    dt = datetime(2024, 1, 1, 14, 30, tzinfo=timezone.utc)
    # Aggiorna il test per considerare il default del timezone del runner di GitHub Actions
    assert format_local(dt) == '14:30 UTC'

def test_format_local_time_github_actions():
    dt = datetime(2024, 1, 1, 14, 30, tzinfo=timezone.utc)
    # Aggiorna il test per considerare il default del timezone del runner di GitHub Actions
    assert format_local(dt) == '14:30 UTC'