from datetime import timezone
from zoneinfo import ZoneInfo


def hours_between(start, end, tz_name="Europe/Rome"):
    """Calcola la differenza in ore tra due datetime, secondo il fuso indicato (per test_050)."""
    tz = ZoneInfo(tz_name)
    # Conversione esplicita a UTC prima della sottrazione: sottrarre due
    # datetime con lo stesso tzinfo fa ignorare a Python l'offset (DST escluso).
    start = start.astimezone(tz).astimezone(timezone.utc)
    end = end.astimezone(tz).astimezone(timezone.utc)
    return (end - start).total_seconds() / 3600
