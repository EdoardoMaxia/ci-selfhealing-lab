import json
from pathlib import Path


def parse_sample(base_dir):
    """Reads and parses the requested JSON fixture (for test_027)."""
    path = Path(base_dir) / "fixtures" / "sample.json"
    return json.loads(path.read_text(encoding="utf-8"))
