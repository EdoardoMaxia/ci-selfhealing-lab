"""
--verify-dep-config (failing-state verification for dependency/config, MSR revision §9a).

Deterministic: no LLM, no GitHub (client functions are faked). The injection
tests touch the working tree like test_benchmark_inject_error.py and restore it.

Run:  python -m pytest agent/tests/test_verify_dep_config.py -v
"""
import csv
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from agent.github import client
from experiments import benchmark, protocol_b
from experiments.dataset import DATASET

REPO_ROOT = Path(__file__).resolve().parents[2]


def _head_blobs():
    """Remote tree faked as HEAD: the local clean tree has no differences."""
    out = subprocess.run(["git", "ls-tree", "-r", "HEAD", "--", *protocol_b.CI_SCOPE],
                         cwd=REPO_ROOT, capture_output=True, text=True, check=True).stdout
    return {line.split("\t")[1]: line.split()[2] for line in out.splitlines()}


# ── CLI ───────────────────────────────────────────────────────

def test_help_shows_flags():
    out = subprocess.run([sys.executable, "experiments/benchmark.py", "--help"], cwd=REPO_ROOT,
                         capture_output=True, text=True, timeout=120).stdout
    for flag in ("--verify-dep-config", "--verify-batch", "--no-run-timeout"):
        assert flag in out


def test_test_category_rejected():
    proc = subprocess.run([sys.executable, "experiments/benchmark.py", "--verify-dep-config", "--category", "test"],
                          cwd=REPO_ROOT, capture_output=True, text=True, timeout=120)
    assert proc.returncode == 2 and "dependency and config" in proc.stderr


def test_runner_script():
    script = REPO_ROOT / "experiments" / "run_verify_dep_config.sh"
    assert os.access(script, os.X_OK)
    assert subprocess.run(["bash", "-n", str(script)]).returncode == 0
    text = script.read_text()
    assert "--verify-dep-config --category" in text and "fix/ai-" in text


# ── classification and static workflow check ──────────────────

@pytest.mark.parametrize("appeared,conclusion,control,expected", [
    (True, "failure", True, ("failure", True)),
    (True, "startup_failure", True, ("startup_failure", True)),
    (False, None, True, ("no_run", True)),
    (False, None, False, ("no_run", False)),
    (True, "success", True, ("success", False)),
    (True, None, True, ("error", False)),
    (True, "cancelled", True, ("cancelled", False)),
])
def test_classify_failing_state(appeared, conclusion, control, expected):
    concl, ok, note = protocol_b.classify_failing_state(appeared, conclusion, control)
    assert (concl, ok) == expected
    if concl == "success":
        assert "ANOMALY" in note


@pytest.mark.parametrize("pattern,ref,match", [
    ("fix/**", "fix/ai-verify-x", True), ("fix/*", "fix/ai-verify-x", True),
    ("fix/*", "fix/a/b", False), ("main", "fix/ai-verify-x", False), ("**", "fix/a/b", True),
])
def test_gh_branch_match(pattern, ref, match):
    assert protocol_b.gh_branch_match(pattern, ref) is match


def test_workflow_check():
    baseline = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert protocol_b.workflow_check(baseline) == "ok"
    assert protocol_b.workflow_check("jobs: [\n").startswith("yaml_error")
    assert "does not match" in protocol_b.workflow_check(
        "on:\n  push:\n    branches: [main]\njobs:\n  t:\n    runs-on: x\n")
    assert protocol_b.workflow_check("on: pull_request\njobs:\n  t: {}\n") == "no push trigger"


# ── preparing the failing states (real injection, nothing pushed) ──

def test_prepare_failing_states(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    dep = next(e for e in DATASET if e["id"] == "dep_001")
    fake_conf = {"id": "conf_x", "category": "config", "difficulty": "easy",
                 "git_diff": "-    line-not-in-ci-yml\n+    something-else"}
    try:
        states = benchmark.prepare_failing_states([dep, fake_conf], _head_blobs())
    finally:
        benchmark.reset_files()
    assert list(states[0]["changes"]) == ["requirements.txt"]
    assert b"numpy==99.99.99" in states[0]["changes"]["requirements.txt"]
    assert states[1]["changes"] == {}                       # injection changed nothing
    assert states[1]["workflow_check"] == "ok"
    assert subprocess.run(["git", "status", "--porcelain", "--", *protocol_b.CI_SCOPE],
                          cwd=REPO_ROOT, capture_output=True, text=True).stdout == ""


# ── the whole mode with a fake GitHub ─────────────────────────

class FakeGitHub:
    """commit -> sha; scripted CI outcome per branch prefix; records pushes and deletions."""
    def __init__(self, outcomes):
        self.outcomes, self.pushed, self.deleted, self.waits = outcomes, {}, [], []

    def commit(self, repo, base_sha, branch, changes, message):
        sha = f"sha-{len(self.pushed)}"
        self.pushed[branch] = (sha, dict(changes))
        return sha

    def wait(self, repo, branch, head_sha, timeout_sec=300, poll_interval=15):
        self.waits.append((branch, timeout_sec))
        key = next(k for k in self.outcomes if branch.startswith(k))
        appeared, conclusion = self.outcomes[key]
        return {"conclusion": conclusion if appeared else None, "status": "completed" if appeared else None,
                "run_id": 100 + len(self.waits) if appeared else None,
                "run_url": "u" if appeared else None, "head_sha": head_sha}


def _install(monkeypatch, fake):
    repo = MagicMock()
    repo.get_branch.return_value.commit.sha = "mainsha"
    monkeypatch.setattr(client, "get_repo", lambda name: repo)
    monkeypatch.setattr(client, "commit_files_on_new_branch", fake.commit)
    monkeypatch.setattr(client, "wait_for_ci_run", fake.wait)
    monkeypatch.setattr(client, "delete_branch", lambda r, b: fake.deleted.append(b))
    monkeypatch.setattr(protocol_b, "remote_scope_blobs", lambda r, sha: _head_blobs())


def test_verify_dep_config_cases(monkeypatch, tmp_path):
    monkeypatch.chdir(REPO_ROOT)
    cases = [next(e for e in DATASET if e["id"] == cid) for cid in ("dep_001", "dep_025", "conf_006")]
    cases.append({"id": "conf_noop", "category": "config", "difficulty": "easy",
                  "git_diff": "-    not-in-file\n+    x"})
    fake = FakeGitHub({"fix/ai-verify-control": (True, "success"),
                       "fix/ai-verify-ctx-": (True, "success"),          # dep_025: clean state + context
                       "fix/ai-verify-dep_001": (True, "failure"),
                       "fix/ai-verify-dep_025": (True, "success"),
                       "fix/ai-verify-conf_006": (False, None),
                       "fix/ai-verify-conf_noop": (True, "success")})
    _install(monkeypatch, fake)
    try:
        rows = benchmark.verify_dep_config_cases(cases, tmp_path, "ts", 300, 120, batch=3)
    finally:
        benchmark.reset_files()
    by = {r["case_id"]: r for r in rows}
    assert (by["dep_001"]["ci_conclusion"], by["dep_001"]["verified_failing"]) == ("failure", True)
    assert (by["dep_025"]["ci_conclusion"], by["dep_025"]["verified_failing"]) == ("success", False)
    assert "ANOMALY" in by["dep_025"]["notes"]
    assert (by["conf_006"]["ci_conclusion"], by["conf_006"]["verified_failing"]) == ("no_run", True)
    assert "control run" in by["conf_006"]["notes"]
    assert by["conf_noop"]["injection_applied"] is False and "injection_noop" in by["conf_noop"]["notes"]
    # F1: a non-injectable case is never pushed (it would be a commit identical to main)
    assert by["conf_noop"]["ci_conclusion"] == "not_injectable" and by["conf_noop"]["branch"] == ""
    assert not any("conf_noop" in b for b in fake.pushed)
    # F1: dep_025 has context_requirements -> its "clean state + context" control is pushed too
    assert by["dep_025"]["context_control_conclusion"] == "success"
    ctx_branch = next(b for b in fake.pushed if b.startswith("fix/ai-verify-ctx-dep_025"))
    assert fake.pushed[ctx_branch][1]["requirements.txt"].decode().splitlines()[-1] == "click==8.1.7"
    # every branch is under fix/ (ci.yml triggers only on main and fix/**) and is deleted
    assert all(b.startswith("fix/ai-verify-") for b in fake.pushed)
    assert sorted(fake.deleted) == sorted(fake.pushed)
    assert fake.pushed[by["dep_001"]["branch"]][1].keys() == {"requirements.txt"}
    assert json.load(open(tmp_path / "verify_control_ts.json"))["conclusion"] == "success"

    merged = benchmark.save_verify_dep_config(rows, tmp_path, "ts")
    out = list(csv.DictReader(open(merged, encoding="utf-8")))
    assert list(out[0]) == benchmark.VERIFY_DC_COLUMNS
    assert {r["case_id"]: r["verified_failing"] for r in out}["dep_001"] == "true"
    # re-running one case replaces only its row
    benchmark.save_verify_dep_config([dict(by["dep_025"], ci_conclusion="failure", verified_failing=True)], tmp_path, "ts2")
    out = {r["case_id"]: r for r in csv.DictReader(open(merged, encoding="utf-8"))}
    assert len(out) == 4 and out["dep_025"]["verified_failing"] == "true" and out["dep_001"]["ci_conclusion"] == "failure"


def test_control_not_green_aborts(monkeypatch, tmp_path):
    monkeypatch.chdir(REPO_ROOT)
    fake = FakeGitHub({"fix/ai-verify-control": (False, None), "fix/ai-verify-": (True, "failure")})
    _install(monkeypatch, fake)
    rows = benchmark.verify_dep_config_cases([next(e for e in DATASET if e["id"] == "dep_001")],
                                             tmp_path, "ts", 300, 120, batch=5)
    assert rows is None
    assert list(fake.pushed) == [b for b in fake.pushed if "control" in b]   # nothing else pushed
