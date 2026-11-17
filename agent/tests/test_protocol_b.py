"""
Protocol B for the "test" category (MSR revision A2, reviewer concern 2).

Deterministic: no LLM, no GitHub (the PyGitHub repo object is faked).
The injection tests touch the working tree like test_benchmark_inject_error.py
and restore it with reset_files().

Run:  python -m pytest agent/tests/test_protocol_b.py -v
"""
import csv
import json
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from agent.github import client
from agent.pipeline import fix_executor
from agent.state import AgentState
from experiments import benchmark, protocol_b
from experiments.dataset import DATASET

REPO_ROOT = Path(__file__).resolve().parents[2]
TEST_CASES = [e for e in DATASET if e["category"] == "test"]


# ── exclusion list ────────────────────────────────────────────

def test_excluded_cases_are_the_11_expected():
    expected = set(benchmark.TEST_TARGET_OVERRIDE) | {"test_012", "test_027"}
    assert set(benchmark.EXCLUDED_TEST_CASES) == expected
    assert len(benchmark.EXCLUDED_TEST_CASES) == 11
    assert all(cid in {e["id"] for e in TEST_CASES} for cid in benchmark.EXCLUDED_TEST_CASES)
    assert len(TEST_CASES) - 11 == 39
    assert len(DATASET) - 11 == 139


def _changed_files():
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--", *protocol_b.CI_SCOPE],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True).stdout
    return sorted(l[3:] for l in out.splitlines() if l.strip())


def test_injection_scope_matches_exclusion_list(monkeypatch):
    """Excluded <=> the injection touches something other than the test file the agent edits."""
    from agent.agents.test_agent import find_test_file
    monkeypatch.chdir(REPO_ROOT)
    benchmark.reset_files()
    assert _changed_files() == [], "working tree under CI_SCOPE must be clean to run this test"
    try:
        for case in TEST_CASES:
            benchmark.reset_files()
            assert benchmark.inject_error(case), case["id"]
            changed = _changed_files()
            agent_file = find_test_file(case["ci_logs"], ".").replace("\\", "/").removeprefix("./")
            if case["id"] in benchmark.EXCLUDED_TEST_CASES:
                assert changed == [benchmark.EXCLUDED_TEST_CASES[case["id"]]], (case["id"], changed)
                assert agent_file not in changed
            else:
                assert changed == [agent_file], (case["id"], changed, agent_file)
    finally:
        benchmark.reset_files()


# ── CLI ───────────────────────────────────────────────────────

def test_help_shows_new_flags():
    out = subprocess.run([sys.executable, "experiments/benchmark.py", "--help"],
                         cwd=REPO_ROOT, capture_output=True, text=True, timeout=120).stdout
    for flag in ("--test-protocol-b", "--verify-excluded", "--output-dir", "--ci-timeout"):
        assert flag in out


def test_protocol_b_rejects_dry_run():
    proc = subprocess.run([sys.executable, "experiments/benchmark.py", "--test-protocol-b", "--dry-run"],
                          cwd=REPO_ROOT, capture_output=True, text=True, timeout=120)
    assert proc.returncode == 2 and "dry-run" in proc.stderr


# ── failed state = local tree vs remote tree ──────────────────

def test_git_blob_sha_matches_git():
    data = b"print('x')\n"
    expected = subprocess.run(["git", "hash-object", "--stdin"], input=data,
                              capture_output=True, check=True).stdout.decode().strip()
    assert client.git_blob_sha(data) == expected


def test_diff_against_remote(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    files = {"src/a.py": b"A = 1\n", "tests/test_a.py": b"def test_a():\n    assert 1\n",
             "tests/fixtures/x.json": b"{}\n", "requirements.txt": b"pytest\n", "README.md": b"r\n"}
    for p, c in files.items():
        (tmp_path / p).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / p).write_bytes(c)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    remote = {p: client.git_blob_sha(c) for p, c in files.items() if protocol_b.in_scope(p)}
    assert "README.md" not in remote

    assert protocol_b.diff_against_remote(remote, tmp_path) == {}

    (tmp_path / "tests/test_a.py").write_bytes(b"def test_a():\n    assert 0\n")   # modified
    (tmp_path / "tests/fixtures/x.json").unlink()                                 # deleted
    (tmp_path / "src/new.py").write_bytes(b"N = 1\n")                             # untracked, added
    (tmp_path / "README.md").write_bytes(b"changed\n")                            # out of scope
    (tmp_path / "src/__pycache__").mkdir()
    (tmp_path / ".gitignore").write_text("__pycache__/\n")
    (tmp_path / "src/__pycache__/a.cpython-312.pyc").write_bytes(b"\0")           # ignored
    assert protocol_b.diff_against_remote(remote, tmp_path) == {
        "src/new.py": b"N = 1\n",
        "tests/fixtures/x.json": None,
        "tests/test_a.py": b"def test_a():\n    assert 0\n",
    }


@pytest.mark.parametrize("conclusion,status", [("success", "green"), ("failure", "red"),
                                               (None, "error"), ("cancelled", "error"),
                                               ("timed_out", "error")])
def test_ci_status(conclusion, status):
    assert protocol_b.ci_status(conclusion) == status


# ── GitHub helpers (fake repo) ────────────────────────────────

def test_commit_files_on_new_branch_builds_one_commit_and_one_ref():
    repo = MagicMock()
    base_commit = MagicMock(sha="base")
    base_commit.tree.sha = "tree0"
    repo.get_git_commit.return_value = base_commit
    repo.get_git_tree.return_value.tree = [
        SimpleNamespace(path="tests/test_a.py", mode="100644", type="blob"),
        SimpleNamespace(path="scripts/run.sh", mode="100755", type="blob"),
    ]
    repo.create_git_blob.side_effect = lambda content, enc: SimpleNamespace(sha=f"blob-{len(content)}")
    repo.create_git_commit.return_value = SimpleNamespace(sha="newcommit")

    sha = client.commit_files_on_new_branch(
        repo, "base", "fix/ai-x",
        {"tests/test_a.py": b"x", "scripts/run.sh": b"y", "gone.txt": None,
         "scripts\\new.py": b"z", "scripts/run2.sh": None},
        "msg")

    assert sha == "newcommit"
    elements = {e._identity["path"]: e._identity for e in repo.create_git_tree.call_args.args[0]}
    assert elements["scripts/run.sh"]["mode"] == "100755"            # mode of the base tree kept
    assert elements["scripts/new.py"]["mode"] == "100644"            # backslashes normalized
    assert "gone.txt" not in elements and "scripts/run2.sh" not in elements   # absent in base: no-op
    assert repo.create_git_tree.call_args.kwargs["base_tree"] is base_commit.tree
    repo.create_git_commit.assert_called_once()
    assert repo.create_git_commit.call_args.args[2] == [base_commit]
    repo.create_git_ref.assert_called_once_with(ref="refs/heads/fix/ai-x", sha="newcommit")


def test_commit_files_on_new_branch_deletes_existing_file():
    repo = MagicMock()
    repo.get_git_tree.return_value.tree = [SimpleNamespace(path="tests/fixtures/s.json", mode="100644", type="blob")]
    client.commit_files_on_new_branch(repo, "base", "b", {"tests/fixtures/s.json": None}, "m")
    (element,) = repo.create_git_tree.call_args.args[0]
    assert element._identity == {"path": "tests/fixtures/s.json", "mode": "100644", "type": "blob", "sha": None}


def _run(id_, sha, status, conclusion=None):
    return SimpleNamespace(id=id_, head_sha=sha, status=status, conclusion=conclusion,
                           html_url=f"https://x/runs/{id_}")


def test_wait_for_ci_run_ignores_runs_of_other_commits(monkeypatch):
    monkeypatch.setattr(client.time, "sleep", lambda s: None)
    polls = [
        # the branch-creation run of the base commit is already completed and green
        [_run(1, "base", "completed", "success")],
        [_run(1, "base", "completed", "success"), _run(2, "fix", "in_progress")],
        [_run(1, "base", "completed", "success"), _run(2, "fix", "completed", "failure")],
    ]
    repo = MagicMock()
    repo.get_workflow_runs.side_effect = lambda **kw: polls.pop(0)
    out = client.wait_for_ci_run(repo, "fix/ai-x", head_sha="fix", timeout_sec=100, poll_interval=1)
    assert out["conclusion"] == "failure" and out["run_id"] == 2 and out["head_sha"] == "fix"
    assert repo.get_workflow_runs.call_args.kwargs == {"branch": "fix/ai-x", "head_sha": "fix", "event": "push"}


def test_wait_for_ci_run_timeout(monkeypatch):
    monkeypatch.setattr(client.time, "sleep", lambda s: None)
    repo = MagicMock()
    repo.get_workflow_runs.return_value = [_run(7, "fix", "queued")]
    out = client.wait_for_ci_run(repo, "b", head_sha="fix", timeout_sec=30, poll_interval=15)
    assert out["conclusion"] is None and out["run_id"] == 7


# ── Fix Executor ──────────────────────────────────────────────

def test_agent_state_declares_protocol_b_fields():
    assert {"fix_base_sha", "ci_runs"} <= set(AgentState.__annotations__)


def _write_scratch():
    scratch = REPO_ROOT / "tests" / "test_protocol_b_scratch.py"
    scratch.write_text("def test_x():\n    assert True\n", encoding="utf-8")
    return scratch


def test_fix_executor_branches_from_failed_state_when_base_sha_set(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    scratch = _write_scratch()
    state = {"repo_name": "o/r", "repo_path": ".", "error_category": "test",
             "modified_file": "tests/test_protocol_b_scratch.py", "commit_sha": "abc1234",
             "attempt_number": 2, "fix_base_sha": "precheck", "ci_runs": [{"attempt": 0}]}
    try:
        with patch.object(fix_executor, "get_repo") as get_repo, \
             patch.object(fix_executor, "create_branch") as create_branch, \
             patch.object(fix_executor, "commit_file") as commit_file, \
             patch.object(fix_executor, "wait_for_ci") as wait_for_ci, \
             patch.object(fix_executor, "commit_files_on_new_branch", return_value="fixsha") as cf, \
             patch.object(fix_executor, "wait_for_ci_run",
                          return_value={"conclusion": "success", "run_id": 9, "run_url": "u",
                                        "status": "completed", "head_sha": "fixsha"}) as wr:
            out = fix_executor.fix_executor_node(state)
    finally:
        scratch.unlink()
    create_branch.assert_not_called(); commit_file.assert_not_called(); wait_for_ci.assert_not_called()
    get_repo.return_value.get_branch.assert_not_called()              # main is never the base
    repo, base, branch, changes, _msg = cf.call_args.args
    assert base == "precheck" and branch.startswith("fix/ai-test-")
    assert changes == {"tests/test_protocol_b_scratch.py": b"def test_x():\n    assert True\n"}
    assert wr.call_args.kwargs["head_sha"] == "fixsha"
    assert out["ci_fixed"] is True
    assert out["ci_runs"][-1] | {} == {"attempt": 1, "branch": branch, "base_sha": "precheck",
                                       "commit_sha": "fixsha", "file": "tests/test_protocol_b_scratch.py",
                                       "run_id": 9, "run_url": "u", "conclusion": "success"}
    assert len(out["ci_runs"]) == 2


def test_fix_executor_default_protocol_unchanged(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    scratch = _write_scratch()
    state = {"repo_name": "o/r", "repo_path": ".", "error_category": "test",
             "modified_file": "tests/test_protocol_b_scratch.py", "commit_sha": "abc1234",
             "attempt_number": 2}
    try:
        with patch.object(fix_executor, "get_repo") as get_repo, \
             patch.object(fix_executor, "create_branch") as create_branch, \
             patch.object(fix_executor, "commit_file"), \
             patch.object(fix_executor, "wait_for_ci", return_value=False), \
             patch.object(fix_executor, "commit_files_on_new_branch") as cf:
            get_repo.return_value.get_branch.return_value.commit.sha = "mainsha"
            out = fix_executor.fix_executor_node(state)
    finally:
        scratch.unlink()
    cf.assert_not_called()
    assert create_branch.call_args.args[1] == "mainsha"
    assert set(out) == {"ci_fixed", "fix_branch"}


# ── assertions ────────────────────────────────────────────────

ORIGINAL = '''
import pytest
from src.x import f

def test_one():
    assert f(1) == 2
    assert f(2) == 4

def test_raises():
    with pytest.raises(ValueError):
        f(-1)

class TestX:
    def test_mock(self):
        self.assertEqual(f(3), 6)
'''


def test_extract_assertions_kinds_and_scopes():
    found = protocol_b.extract_assertions(ORIGINAL)
    assert [(a["scope"], a["text"]) for a in found] == [
        ("test_one", "assert f(1) == 2"),
        ("test_one", "assert f(2) == 4"),
        ("test_raises", "pytest.raises(ValueError)"),
        ("TestX.test_mock", "self.assertEqual(f(3), 6)"),
    ]


def test_compare_assertions_identical_and_formatting():
    reformatted = ORIGINAL.replace("assert f(1) == 2", "assert f( 1 )==2")
    out = protocol_b.compare_assertions(ORIGINAL, reformatted)
    assert out["summary"] == "4/0/0" and out["counts"]["added"] == 0


def test_compare_assertions_modified_removed_added_moved():
    repaired = '''
import pytest
from src.x import f

def test_one_renamed():
    assert f(1) == 2

def test_raises():
    f(-1)

class TestX:
    def test_mock(self):
        self.assertEqual(f(3), 7)
        assert True
'''
    out = protocol_b.compare_assertions(ORIGINAL, repaired)
    # kept: f(1)==2 (moved to test_one_renamed); modified: assertEqual 6 -> 7;
    # removed: f(2)==4 and pytest.raises; added: assert True
    assert out["summary"] == "1/1/2"
    assert out["kept"][0]["moved_to"] == "test_one_renamed"
    assert out["modified"] == [{"scope": "TestX.test_mock", "original": "self.assertEqual(f(3), 6)",
                                "repaired": "self.assertEqual(f(3), 7)"}]
    assert {r["text"] for r in out["removed"]} == {"assert f(2) == 4", "pytest.raises(ValueError)"}
    assert out["added"] == [{"scope": "TestX.test_mock", "text": "assert True"}]


def test_compare_assertions_parse_error():
    assert protocol_b.compare_assertions(ORIGINAL, "def broken(:\n")["summary"] == "parse_error"


def test_assertions_report_uses_baseline_as_reference():
    injected = ORIGINAL.replace("== 4", "== 5")
    summary, detail = protocol_b.assertions_report(ORIGINAL, injected, ORIGINAL)
    detail = json.loads(detail)
    assert summary == "4/0/0"
    assert detail["vs_injected"]["summary"] == "3/1/0"


# ── clean source ──────────────────────────────────────────────

def test_run_test_on_clean_source_pass_and_fail():
    rel = "tests/test_calculator.py"
    good = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=REPO_ROOT,
                          capture_output=True, check=True).stdout
    assert protocol_b.run_test_on_clean_source(rel, good, REPO_ROOT)["result"] == "pass"
    bad = good + b"\n\ndef test_wrong():\n    assert add(2, 2) == 5\n"
    out = protocol_b.run_test_on_clean_source(rel, bad, REPO_ROOT)
    assert out["result"] == "fail" and "1 failed" in out["summary"]
    assert protocol_b.run_test_on_clean_source(rel, b"def x(:\n", REPO_ROOT)["result"] == "fail"


# ── one protocol-B case end to end (GitHub + graph faked) ─────

MODEL = {"id": "fake", "name": "Fake", "type": "t", "provider": "anthropic", "timeout": 60}


def test_protocol_b_excluded_case_row():
    case = next(e for e in TEST_CASES if e["id"] == "test_012")
    row = benchmark.run_test_case_protocol_b(MODEL, case, True, False, 60, 60)
    assert row["final_status"] == "excluded" and row["excluded"] is True and row["valid_case"] == 0
    assert "src/db.py" in row["exclusion_reason"]
    assert set(benchmark.PROTOCOL_B_COLUMNS) <= set(row)


def _fake_precheck(status):
    def fake(repo, error, ci_timeout):
        changes = protocol_b.diff_against_remote(
            {p: client.git_blob_sha(subprocess.run(["git", "show", f"HEAD:{p}"], capture_output=True).stdout)
             for p in protocol_b.local_scope_files()})
        return {"status": status, "sha": "pre123", "run_id": 11, "run_url": "u", "branch": "fix/ai-precheck-x",
                "base_sha": "main", "changes": changes}
    return fake


def test_protocol_b_valid_case_row_and_csv(monkeypatch, tmp_path):
    monkeypatch.chdir(REPO_ROOT)
    case = next(e for e in TEST_CASES if e["id"] == "test_010")   # tests/test_api.py
    rel = "tests/test_api.py"
    seen = {}

    def fake_run_single_error(error, dry_run, no_memory, readonly_memory, fix_base_sha):
        seen["base"] = fix_base_sha
        Path(rel).write_text(subprocess.run(["git", "show", f"HEAD:{rel}"], capture_output=True,
                                            text=True).stdout)          # perfect repair
        return {"error_id": error["id"], "category": "test", "difficulty": error["difficulty"],
                "final_status": "fixed", "success": 1, "router_category": "test", "router_correct": 1,
                "router_confidence": 0.9, "router_reasoning": "", "attempts_count": 1, "fix_attempt": 1,
                "json_parse_fail": 0, "latency_sec": 1.0, "memory_hits": 0, "memory_active": 0,
                "ci_runs": [{"attempt": 1, "commit_sha": "fix1", "run_id": 22, "conclusion": "success"}],
                "modified_file": rel}

    deleted = []
    monkeypatch.setattr(benchmark, "ci_precheck", _fake_precheck("red"))
    monkeypatch.setattr(benchmark, "run_single_error", fake_run_single_error)
    monkeypatch.setattr(client, "get_repo", lambda name: MagicMock())
    monkeypatch.setattr(client, "delete_branch", lambda repo, b: deleted.append(b))
    try:
        row = benchmark.run_test_case_protocol_b(MODEL, case, True, False, 60, 60)
    finally:
        benchmark.reset_files()

    assert seen["base"] == "pre123" and deleted == ["fix/ai-precheck-x"]
    assert row["valid_case"] == 1 and row["final_status"] == "fixed"
    assert json.loads(row["injected_files"]) == [rel]
    assert (row["pre_ci_status"], row["pre_ci_sha"], row["pre_ci_run_id"]) == ("red", "pre123", 11)
    assert (row["post_ci_status"], row["post_ci_sha"], row["post_ci_run_id"]) == ("green", "fix1", 22)
    assert row["agent_modified_file"] == rel and row["agent_file_is_injected"] is True
    assert row["test_on_clean_source"] == "pass"
    detail = json.loads(row["assertions_detail"])
    assert row["assertions_preserved"] == f"{detail['vs_baseline']['counts']['original']}/0/0"
    assert detail["vs_injected"]["counts"]["modified"] == 1          # the injection changed one assert
    assert "ci_runs" not in row and "modified_file" not in row

    excluded = benchmark.run_test_case_protocol_b(
        MODEL, next(e for e in TEST_CASES if e["id"] == "test_009"), True, False, 60, 60)
    csv_path = benchmark.save_results([row, excluded], "unit", tmp_path)
    with open(csv_path, newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    for col in ["pre_ci_status", "pre_ci_sha", "pre_ci_run_id", "post_ci_status", "post_ci_sha",
                "post_ci_run_id", "test_on_clean_source", "assertions_preserved",
                "assertions_detail", "excluded", "exclusion_reason"]:
        assert col in header


def test_protocol_b_green_precheck_is_skipped(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    case = next(e for e in TEST_CASES if e["id"] == "test_001")
    called = []
    monkeypatch.setattr(benchmark, "ci_precheck", _fake_precheck("green"))
    monkeypatch.setattr(benchmark, "run_single_error", lambda *a: called.append(a))
    monkeypatch.setattr(client, "get_repo", lambda name: MagicMock())
    monkeypatch.setattr(client, "delete_branch", lambda repo, b: None)
    try:
        row = benchmark.run_test_case_protocol_b(MODEL, case, True, False, 60, 60)
    finally:
        benchmark.reset_files()
    assert called == [] and row["final_status"] == "precheck_green" and row["valid_case"] == 0


def test_save_results_union_of_columns(tmp_path):
    path = benchmark.save_results([{"a": 1}, {"a": 2, "b": 3}], "u", tmp_path)
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    assert rows == [{"a": "1", "b": ""}, {"a": "2", "b": "3"}]
