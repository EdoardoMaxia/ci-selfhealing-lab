from pathlib import Path


def load_csv(base_dir):
    """Legge il file dati con un path relativo alla directory del chiamante (per test_025)."""
    path = Path(base_dir) / "data" / "sample.csv"
    return path.read_text(encoding="utf-8")
