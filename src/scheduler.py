from datetime import timezone


def format_local(dt):
    """Formats a datetime in UTC, independent of the runner's timezone (for test_041)."""
    return dt.astimezone(timezone.utc).strftime('%H:%M UTC')
