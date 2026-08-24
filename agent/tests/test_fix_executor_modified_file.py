"""
Regressione — il campo modified_file deve essere dichiarato in AgentState
(altrimenti LangGraph lo scarta silenziosamente) e il Fix Executor deve
usarlo quando presente, con fallback su AGENT_FILE_MAP solo se assente/vuoto.

Prima del fix (vedi git history di agent/state.py) modified_file non era
nel TypedDict: il Test Agent non poteva comunicare al Fix Executor quale
file aveva realmente modificato quando diverso dal path di default
tests/test_calculator.py.

GitHub non viene mai contattato realmente: get_repo/create_branch/
commit_file/wait_for_ci sono mockati.

repo_path e' sempre "." nell'uso reale (vedi experiments/benchmark.py e
agent/pipeline/context_builder.py) — i test replicano questa condizione
invece di un path assoluto arbitrario, dato che la logica di
relativizzazione in fix_executor_node si basa su quell'assunzione.
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

from agent.state import AgentState
from agent.pipeline.fix_executor import fix_executor_node, AGENT_FILE_MAP

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_agent_state_declares_modified_file():
    assert "modified_file" in AgentState.__annotations__, (
        "modified_file non e' dichiarato in AgentState: LangGraph lo "
        "scarterebbe silenziosamente quando un agente lo valorizza"
    )


def _mock_repo():
    repo = MagicMock()
    repo.get_branch.return_value.commit.sha = "deadbeef"
    return repo


def test_fix_executor_uses_modified_file_when_present():
    scratch = REPO_ROOT / "tests" / "test_bug3_regression_scratch.py"
    scratch.write_text("def test_x():\n    assert True\n", encoding="utf-8")

    state = {
        "repo_name":      "owner/repo",
        "repo_path":      ".",
        "error_category": "test",
        "modified_file":  "tests/test_bug3_regression_scratch.py",
        "commit_sha":     "abc123",
        "attempt_number": 2,
    }

    try:
        with patch("agent.pipeline.fix_executor.get_repo", return_value=_mock_repo()), \
             patch("agent.pipeline.fix_executor.create_branch"), \
             patch("agent.pipeline.fix_executor.commit_file") as mock_commit_file, \
             patch("agent.pipeline.fix_executor.wait_for_ci", return_value=True):
            fix_executor_node(state)
    finally:
        scratch.unlink()

    committed_path = mock_commit_file.call_args.args[2]
    assert committed_path == "tests/test_bug3_regression_scratch.py"
    assert "\\" not in committed_path
    assert committed_path != AGENT_FILE_MAP["test"]


def test_fix_executor_falls_back_to_agent_file_map_when_absent():
    # tests/test_calculator.py esiste gia' nella baseline del repo: non va
    # ne' creato ne' ripulito.
    state = {
        "repo_name":      "owner/repo",
        "repo_path":      ".",
        "error_category": "test",
        "modified_file":  "",
        "commit_sha":     "abc123",
        "attempt_number": 1,
    }

    with patch("agent.pipeline.fix_executor.get_repo", return_value=_mock_repo()), \
         patch("agent.pipeline.fix_executor.create_branch"), \
         patch("agent.pipeline.fix_executor.commit_file") as mock_commit_file, \
         patch("agent.pipeline.fix_executor.wait_for_ci", return_value=True):
        fix_executor_node(state)

    committed_path = mock_commit_file.call_args.args[2]
    assert committed_path == AGENT_FILE_MAP["test"]
