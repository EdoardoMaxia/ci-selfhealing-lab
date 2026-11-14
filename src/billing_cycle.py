from datetime import timezone
from zoneinfo import ZoneInfo


def hours_between(start, end, tz_name="Europe/Rome"):
    """Computes the difference in hours between two datetimes, in the given timezone (for test_050)."""
    tz = ZoneInfo(tz_name)
    # Explicit conversion to UTC before subtracting: subtracting two
    # datetimes with the same tzinfo makes Python ignore the offset (DST excluded).
    start = start.astimezone(tz).astimezone(timezone.utc)
    end = end.astimezone(tz).astimezone(timezone.utc)
    return (end - start).total_seconds() / 3600
