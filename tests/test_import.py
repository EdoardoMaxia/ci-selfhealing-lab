import json
from pathlib import Path


def test_parse_sample():
    path = Path(__file__).parent / 'fixtures' / 'sample.json'
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"key": "value"}), encoding='utf-8')
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data["key"] == "value"