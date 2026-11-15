import json
from pathlib import Path


def test_parse_sample():
    path = Path(__file__).parent / 'fixtures' / 'sample.json'
    if not path.exists():
        pytest.skip("sample.json file is missing")
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data["key"] == "value"