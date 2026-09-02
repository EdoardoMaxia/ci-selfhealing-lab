from datetime import datetime
from src.serializer import serialize_date

def test_json_serialize():
    d = datetime(2024, 1, 15)
    assert serialize_date(d) == '2024-01-15T00:00:00'

def test_json_serialize_without_time():
    d = datetime(2024, 1, 15)
    assert serialize_date(d) == '2024-01-15'

def test_json_serialize_with_time_component():
    d = datetime(2024, 1, 15, 12, 30)
    assert serialize_date(d) == '2024-01-15T12:30:00'