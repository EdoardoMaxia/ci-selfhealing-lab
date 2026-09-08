import json


def test_parse_sample():
    data = json.loads('{"key": "value"}')
    assert data["key"] == "value"