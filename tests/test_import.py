import json
from pathlib import Path


def test_parse_sample():
    path = Path(__file__).parent / 'fixtures' / 'sample.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data["key"] == "value"
