import json
from pathlib import Path
import pytest


@pytest.mark.skip(reason="sample.json file is missing")
def test_parse_sample():
    path = Path(__file__).parent / 'fixtures' / 'sample.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data["key"] == "value"