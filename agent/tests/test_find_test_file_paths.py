"""
Regressione — find_test_file() deve restituire sempre path con forward
slash, anche su Windows, in tutti i suoi rami (match diretto, fallback
regex, fallback finale hardcoded).

Prima del fix (vedi git history di agent/agents/test_agent.py) i path
potevano contenere backslash letterali: il Fix Executor li committa su
GitHub via API creando un file con nome errato nel repository
(es. "tests\\test_calculator.py" invece di "tests/test_calculator.py").
"""
import pytest

from agent.agents.test_agent import find_test_file


@pytest.mark.parametrize(
    "ci_logs,expected",
    [
        # match diretto su 'FAILED <path>'
        (
            "FAILED tests/test_advanced.py::test_x - AssertionError: assert 1 == 2",
            "tests/test_advanced.py",
        ),
        # fallback regex 'tests/<nome>.py' senza prefisso FAILED
        (
            "qualche log rumoroso\ntests/test_orders.py altro rumore",
            "tests/test_orders.py",
        ),
        # fallback finale hardcoded (nessun path riconoscibile nei log)
        (
            "nessun path di test riconoscibile in questo log",
            "tests/test_calculator.py",
        ),
    ],
)
def test_find_test_file_never_returns_backslash(ci_logs, expected):
    result = find_test_file(ci_logs, ".")
    assert "\\" not in result, f"path con backslash Windows: {result!r}"
    assert result == expected
