from pathlib import Path


def load_csv(base_dir):
    """Reads the data file with a path relative to the caller's directory (for test_025)."""
    path = Path(base_dir) / "data" / "sample.csv"
    return path.read_text(encoding="utf-8")
