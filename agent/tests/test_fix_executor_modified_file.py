"""
Regression — the modified_file field must be declared in AgentState
(otherwise LangGraph silently drops it) and the Fix Executor must
use it when present, falling back to AGENT_FILE_MAP only if missing/empty.

Before the fix (see the git history of agent/state.py) modified_file was not
in the TypedDict: the Test Agent could not tell the Fix Executor which
file it had actually modified when different from the default path
tests/test_calculator.py.

GitHub is never actually contacted: get_repo/create_branch/
commit_file/wait_for_ci are mocked.

repo_path is always "." in real usage (see experiments/benchmark.py and
agent/pipeline/context_builder.py) — the tests replicate this condition
instead of an arbitrary absolute path, since the path relativization
logic in fix_executor_node relies on that assumption.
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

from agent.state import AgentState
from agent.pipeline.fix_executor import fix_executor_node, AGENT_FILE_MAP

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_agent_state_declares_modified_file():
    assert "modified_file" in AgentState.__annotations__, (
        "modified_file is not declared in AgentState: LangGraph would "
        "silently drop it when an agent sets it"
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
    # tests/test_calculator.py already exists in the repo baseline: it must
    # be neither created nor cleaned up.
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
