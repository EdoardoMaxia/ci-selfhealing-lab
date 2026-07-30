import json
from pathlib import Path


def parse_sample(base_dir):
    """Legge e parsifica la fixture JSON richiesta (per test_027)."""
    path = Path(base_dir) / "fixtures" / "sample.json"
    return json.loads(path.read_text(encoding="utf-8"))
