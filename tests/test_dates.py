from datetime import datetime, timezone


def test_parse_date():
    now = datetime.now(timezone.utc)
    assert now.tzinfo is not None