"""
Regressione — inject_error() per category="test" deve modificare
realmente il file di test target, cosi' che la CI fallisca davvero.

Prima del fix (vedi git history di experiments/benchmark.py), inject_error()
era un no-op per questa categoria: la CI non veniva mai rotta e il sistema
"riparava" qualcosa che non era mai stato guasto, producendo un Success Rate
del 100% artificiale su "test".
"""
import subprocess
import sys
from pathlib import Path

from experiments.benchmark import inject_error, reset_files
from experiments.dataset import DATASET

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_inject_error_modifies_test_file_and_breaks_pytest():
    case = next(e for e in DATASET if e["id"] == "test_001")
    target = REPO_ROOT / "tests" / "test_calculator.py"

    reset_files()
    original_content = target.read_text(encoding="utf-8")
    try:
        applied = inject_error(case)
        assert applied is True, "inject_error() deve segnalare l'injection come applicata"

        injected_content = target.read_text(encoding="utf-8")
        assert injected_content != original_content, (
            "inject_error() non ha modificato il file di test target "
            "(no-op sulla categoria 'test')"
        )

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_calculator.py", "-q"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, (
            "la CI dovrebbe fallire dopo l'injection, invece pytest e' verde:\n"
            f"{result.stdout}"
        )
        assert "failed" in result.stdout.lower()
    finally:
        reset_files()
        assert target.read_text(encoding="utf-8") == original_content
