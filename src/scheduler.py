from datetime import timezone


def format_local(dt):
    """Formatta un datetime in UTC, indipendente dal timezone del runner (per test_041)."""
    return dt.astimezone(timezone.utc).strftime('%H:%M UTC')
