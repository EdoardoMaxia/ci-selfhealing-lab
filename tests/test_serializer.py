from datetime import datetime
from src.serializer import serialize_date


def test_json_serialize():
    d = datetime(2024, 1, 15)
    assert serialize_date(d) == '2024-01-15T00:00:00'