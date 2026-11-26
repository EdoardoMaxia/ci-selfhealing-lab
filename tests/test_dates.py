from datetime import datetime, timezone


def test_parse_date():
    now = datetime.utcnow()
    assert now.tzinfo is not None
