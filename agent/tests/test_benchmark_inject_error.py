"""
Regression — inject_error() for category="test" must actually modify
the target test file, so that the CI really fails.

Before the fix (see the git history of experiments/benchmark.py), inject_error()
was a no-op for this category: the CI was never broken and the system
"repaired" something that had never been broken, producing an artificial
100% Success Rate on "test".
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
        assert applied is True, "inject_error() must report the injection as applied"

        injected_content = target.read_text(encoding="utf-8")
        assert injected_content != original_content, (
            "inject_error() did not modify the target test file "
            "(no-op on the 'test' category)"
        )

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_calculator.py", "-q"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, (
            "the CI should fail after the injection, but pytest is green:\n"
            f"{result.stdout}"
        )
        assert "failed" in result.stdout.lower()
    finally:
        reset_files()
        assert target.read_text(encoding="utf-8") == original_content
