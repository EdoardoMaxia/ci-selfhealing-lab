"""
Regression — find_test_file() must always return paths with forward
slashes, even on Windows, in all of its branches (direct match, regex
fallback, final hardcoded fallback).

Before the fix (see the git history of agent/agents/test_agent.py) paths
could contain literal backslashes: the Fix Executor commits them to
GitHub via the API, creating a file with a wrong name in the repository
(e.g. "tests\\test_calculator.py" instead of "tests/test_calculator.py").
"""
import pytest

from agent.agents.test_agent import find_test_file


@pytest.mark.parametrize(
    "ci_logs,expected",
    [
        # direct match on 'FAILED <path>'
        (
            "FAILED tests/test_advanced.py::test_x - AssertionError: assert 1 == 2",
            "tests/test_advanced.py",
        ),
        # regex fallback 'tests/<name>.py' without the FAILED prefix
        (
            "some noisy log\ntests/test_orders.py more noise",
            "tests/test_orders.py",
        ),
        # final hardcoded fallback (no recognizable path in the logs)
        (
            "no recognizable test path in this log",
            "tests/test_calculator.py",
        ),
    ],
)
def test_find_test_file_never_returns_backslash(ci_logs, expected):
    result = find_test_file(ci_logs, ".")
    assert "\\" not in result, f"path with Windows backslash: {result!r}"
    assert result == expected
