import json
from pathlib import Path


def test_parse_sample():
    path = Path(__file__).parent / 'fixtures' / 'sample.json'
    # Verifica che il file esista prima di leggerlo
    assert path.exists(), f"File non trovato: {path}"
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data["key"] == "value"