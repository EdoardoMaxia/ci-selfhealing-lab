from datetime import datetime
from src.serializer import serialize_date


def test_json_serialize():
    d = datetime(2024, 1, 15)
    assert serialize_date(d) == '{"date": "2024-01-15T00:00:00"}'

def test_json_serialize_isoformat():
    d = datetime(2024, 1, 15)
    assert serialize_date(d) == d.isoformat()

def test_json_serialize_strftime():
    d = datetime(2024, 1, 15)
    assert serialize_date(d) == d.strftime('%Y-%m-%d')