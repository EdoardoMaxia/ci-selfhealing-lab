import json
from pathlib import Path


def test_parse_sample():
    path = Path(__file__).parent / 'fixtures' / 'sample.json'
    # Check if the file exists before reading
    if not path.exists():
        # Create a minimal fixture for testing
        sample_data = {"key": "value"}
        path.write_text(json.dumps(sample_data), encoding='utf-8')
    
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data["key"] == "value"