"""
MSR revision F1: no silent injections, excluded cases, dependency context (D1),
protocol B for every category (--failing-state), clean reference per case.

Deterministic: no LLM, no GitHub (client functions are faked). Tests that inject
touch the working tree like test_benchmark_inject_error.py and restore it.

Run:  python -m pytest agent/tests/test_f1_failing_state.py -v
"""
import csv
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agent.github import client
from experiments import benchmark, protocol_b
from experiments.dataset import DATASET

REPO_ROOT = Path(__file__).resolve().parents[2]
BY_ID = {e["id"]: e for e in DATASET}
CI_YML = ".github/workflows/ci.yml"
MODEL = {"id": "fake", "name": "Fake", "type": "t", "provider": "anthropic", "timeout": 60}
NOOP_CONFIG = {"id": "conf_noop", "category": "config", "difficulty": "easy", "ci_logs": "x",
               "ci_job_name": "x", "git_diff": "-    not-in-ci-yml\n+    something-else"}


@pytest.fixture
def repo_cwd(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    benchmark.reset_files()
    yield
    benchmark.reset_files()


def _scope_status():
    return subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--", *protocol_b.CI_SCOPE],
                          cwd=REPO_ROOT, capture_output=True, text=True).stdout


# ── 1.1 inject_error never succeeds silently ──────────────────

def test_config_noop_returns_false_and_leaves_file(repo_cwd):
    before = Path(CI_YML).read_text(encoding="utf-8")
    assert benchmark.inject_error(NOOP_CONFIG) is False
    assert Path(CI_YML).read_text(encoding="utf-8") == before


def test_dependency_noop_returns_false(repo_cwd):
    case = {"id": "dep_noop", "category": "dependency", "git_diff": "+pytest==7.4.0"}   # already declared
    assert benchmark.inject_error(case) is False
    assert Path("requirements.txt").read_text(encoding="utf-8") == benchmark.ORIGINAL_REQUIREMENTS


def test_valid_injections_return_true(repo_cwd):
    assert benchmark.inject_error(BY_ID["conf_001"]) is True
    assert benchmark.inject_error(BY_ID["dep_001"]) is True


@pytest.mark.parametrize("cid", [e["id"] for e in DATASET if e["category"] == "config"
                                 and e["id"] not in benchmark.EXCLUDED_CASES])
def test_included_config_changes_exactly_one_line(repo_cwd, cid):
    before = Path(CI_YML).read_text(encoding="utf-8").splitlines()
    assert benchmark.setup_case(BY_ID[cid]) is True
    after = Path(CI_YML).read_text(encoding="utf-8").splitlines()
    changed = [(a, b) for a, b in zip(before, after) if a != b]
    assert len(before) == len(after) and len(changed) == 1, changed


def test_group_a_replacement_lands_on_setup_python_of_job_a(repo_cwd):
    """python-version: "3.11" appears 4 times: the first one is in job A."""
    for cid, version in (("conf_001", "3.99"), ("conf_002", "3.17"), ("conf_003", "2.7")):
        benchmark.setup_case(BY_ID[cid])
        lines = Path(CI_YML).read_text(encoding="utf-8").splitlines()
        idx = next(i for i, l in enumerate(lines) if f'python-version: "{version}"' in l)
        job = next(l.strip() for l in reversed(lines[:idx]) if l.startswith("  ") and not l.startswith("   "))
        assert job == "A:", (cid, job)
        assert sum('python-version: "3.11"' in l for l in lines) == 3


def test_every_included_case_is_injectable(repo_cwd):
    bad = [e["id"] for e in DATASET if e["id"] not in benchmark.EXCLUDED_CASES and not benchmark.setup_case(e)]
    assert bad == []


def test_run_model_skips_non_injectable_without_running_the_agent(repo_cwd, monkeypatch):
    called = []
    monkeypatch.setattr(benchmark, "run_single_error", lambda *a, **k: called.append(a))
    rows = benchmark.run_model(MODEL, [NOOP_CONFIG], dry_run=False, no_memory=True, keep_branches=True)
    assert called == []
    assert (rows[0]["final_status"], rows[0]["valid_case"], rows[0]["success"]) == ("injection_failed", 0, 0)


def test_run_model_skips_excluded_cases(repo_cwd, monkeypatch):
    called = []
    monkeypatch.setattr(benchmark, "run_single_error", lambda *a, **k: called.append(a))
    rows = benchmark.run_model(MODEL, [BY_ID["conf_031"], BY_ID["dep_043"]], dry_run=False,
                               no_memory=True, keep_branches=True)
    assert called == []
    assert [r["final_status"] for r in rows] == ["excluded", "excluded"]
    assert all(r["excluded"] is True and r["valid_case"] == 0 and r["exclusion_reason"] for r in rows)


# ── 1.4 exclusion list ────────────────────────────────────────

def test_excluded_cases_file():
    data = json.loads(benchmark.EXCLUDED_CASES_FILE.read_text(encoding="utf-8"))
    cases = data["cases"]
    assert len(cases) == len({c["case_id"] for c in cases}) == 71
    assert data["counts"] == {"dependency": 15, "test": 11, "config": 45}
    for c in cases:
        assert BY_ID[c["case_id"]]["category"] == c["category"]
        assert c["group"] and c["reason"] and "\n" not in c["reason"]
    # the 11 test cases are exactly the A2 exclusions of protocol B
    assert {c["case_id"] for c in cases if c["category"] == "test"} == set(benchmark.EXCLUDED_TEST_CASES)
    included = [e for e in DATASET if e["id"] not in benchmark.EXCLUDED_CASES]
    assert {cat: sum(e["category"] == cat for e in included) for cat in ("dependency", "test", "config")} \
        == {"dependency": 35, "test": 39, "config": 5}


# ── 1.3 dependency context (D1) ───────────────────────────────

D1 = {"dep_012": "typing-extensions==4.2.0", "dep_018": "protobuf==3.20.3",
      "dep_025": "click==8.1.7", "dep_048": "boto3==1.34.10"}


def test_context_only_on_the_d1_cases():
    assert {e["id"]: e["context_requirements"] for e in DATASET if "context_requirements" in e} \
        == {cid: [pin] for cid, pin in D1.items()}


@pytest.mark.parametrize("cid,pin", sorted(D1.items()))
def test_context_is_quoted_in_the_logs_and_not_in_the_diff_as_a_change(cid, pin):
    e = BY_ID[cid]
    name, version = pin.split("==")
    assert name in e["ci_logs"] and version in e["ci_logs"]
    assert not any(l[1:].strip() == pin for l in e["git_diff"].splitlines() if l[:1] in "+-")


def test_setup_case_writes_context_before_the_injection(repo_cwd):
    benchmark.setup_case(BY_ID["dep_048"])
    text = Path("requirements.txt").read_text(encoding="utf-8")
    assert text == benchmark.ORIGINAL_REQUIREMENTS + "boto3==1.34.10\n" + "\nbotocore==1.33.0"
    # the Dependency Agent reads the current requirements.txt from disk: it sees the context
    from agent.agents.dependency_agent import read_requirements
    assert "boto3==1.34.10" in read_requirements(".")


def test_reset_files_removes_the_context(repo_cwd):
    benchmark.setup_case(BY_ID["dep_048"])
    benchmark.reset_files()
    assert Path("requirements.txt").read_text(encoding="utf-8") == benchmark.ORIGINAL_REQUIREMENTS
    assert _scope_status() == ""


# ── 1.6 clean reference per case ──────────────────────────────

def test_reference_state():
    assert benchmark.reference_state(BY_ID["dep_048"]) == (
        "requirements.txt", benchmark.ORIGINAL_REQUIREMENTS + "boto3==1.34.10\n")
    assert benchmark.reference_state(BY_ID["dep_001"]) == ("requirements.txt", benchmark.ORIGINAL_REQUIREMENTS)
    path, text = benchmark.reference_state(BY_ID["conf_001"])
    assert path == CI_YML and text == subprocess.run(["git", "show", f"HEAD:{CI_YML}"], cwd=REPO_ROOT,
                                                     capture_output=True, text=True).stdout
    assert benchmark.reference_state(BY_ID["test_001"]) == (None, None)


def test_repair_matches_reference_normalization():
    e = BY_ID["dep_048"]
    assert benchmark.repair_matches_reference(e, "boto3==1.34.10\n\npytest==7.4.0\npytest-cov==4.1.0\n") is True
    assert benchmark.repair_matches_reference(e, benchmark.ORIGINAL_REQUIREMENTS + "boto3==1.34.10\nbotocore==1.34.10") is False
    assert benchmark.repair_matches_reference(BY_ID["test_001"], "x") is None


def test_reference_states_json_is_up_to_date():
    stored = json.loads((REPO_ROOT / "experiments" / "reference_states.json").read_text(encoding="utf-8"))
    assert stored == benchmark.export_reference_states(DATASET)
    assert len(stored) == 40 and all(cid not in benchmark.EXCLUDED_CASES for cid in stored)


# ── 1.5 protocol B for every category ─────────────────────────

def test_cli_failing_state_flag():
    out = subprocess.run([sys.executable, "experiments/benchmark.py", "--help"], cwd=REPO_ROOT,
                         capture_output=True, text=True, timeout=120).stdout
    assert "--failing-state" in out and "--export-references" in out
    proc = subprocess.run([sys.executable, "experiments/benchmark.py", "--failing-state", "--dry-run"],
                          cwd=REPO_ROOT, capture_output=True, text=True, timeout=120)
    assert proc.returncode == 2 and "--failing-state" in proc.stderr


def test_run_model_failing_state_routes_every_category_to_protocol_b(repo_cwd, monkeypatch):
    seen = []
    monkeypatch.setattr(benchmark, "run_case_protocol_b",
                        lambda model, error, *a: seen.append(error["id"]) or {"final_status": "excluded"})
    cases = [BY_ID[c] for c in ("dep_048", "conf_001", "test_001")]
    benchmark.run_model(MODEL, cases, dry_run=False, no_memory=True, keep_branches=True, failing_state=True)
    assert seen == ["dep_048", "conf_001", "test_001"]
    seen.clear()   # --test-protocol-b alone keeps the default protocol for dependency/config
    monkeypatch.setattr(benchmark, "run_single_error", lambda *a, **k: {"final_status": "fixed", "success": 1})
    benchmark.run_model(MODEL, cases, dry_run=False, no_memory=True, keep_branches=True, test_protocol_b=True)
    assert seen == ["test_001"]


def _fake_precheck(status):
    def fake(repo, error, ci_timeout):
        changes = protocol_b.diff_against_remote(
            {p: client.git_blob_sha(subprocess.run(["git", "show", f"HEAD:{p}"], capture_output=True).stdout)
             for p in protocol_b.local_scope_files()})
        return {"status": status, "sha": "pre123", "run_id": 11, "run_url": "u", "branch": "fix/ai-precheck-x",
                "base_sha": "main", "changes": changes}
    return fake


def _agent(router, write):
    def fake_run_single_error(error, dry_run, no_memory, readonly_memory, fix_base_sha):
        assert fix_base_sha == "pre123"
        path, text = write
        Path(path).write_text(text, encoding="utf-8")
        return {"error_id": error["id"], "category": error["category"], "difficulty": error["difficulty"],
                "final_status": "fixed", "success": 1, "router_category": router,
                "router_correct": int(router == error["category"]), "router_confidence": 0.9,
                "router_reasoning": "", "attempts_count": 1, "fix_attempt": 1, "json_parse_fail": 0,
                "latency_sec": 1.0, "memory_hits": 0, "memory_active": 0,
                "ci_runs": [{"attempt": 1, "commit_sha": "fix1", "run_id": 22, "conclusion": "success"}],
                "modified_file": None}
    return fake_run_single_error


def _install(monkeypatch, precheck="red"):
    deleted = []
    monkeypatch.setattr(benchmark, "ci_precheck", _fake_precheck(precheck))
    monkeypatch.setattr(client, "get_repo", lambda name: MagicMock())
    monkeypatch.setattr(client, "delete_branch", lambda repo, b: deleted.append(b))
    return deleted


def test_failing_state_dependency_row(repo_cwd, monkeypatch, tmp_path):
    e = BY_ID["dep_048"]
    deleted = _install(monkeypatch)
    _, ref = benchmark.reference_state(e)
    monkeypatch.setattr(benchmark, "run_single_error", _agent("dependency", ("requirements.txt", ref)))
    row = benchmark.run_case_protocol_b(MODEL, e, True, False, 60, 60)
    assert deleted == ["fix/ai-precheck-x"] and row["valid_case"] == 1
    assert json.loads(row["injected_files"]) == ["requirements.txt"]
    assert (row["category"], row["router_category"]) == ("dependency", "dependency")
    assert (row["pre_ci_status"], row["pre_ci_sha"], row["pre_ci_run_id"]) == ("red", "pre123", 11)
    assert (row["post_ci_status"], row["post_ci_sha"], row["post_ci_run_id"]) == ("green", "fix1", 22)
    assert row["agent_modified_file"] == "requirements.txt" and row["agent_file_is_injected"] is True
    assert row["reference_file"] == "requirements.txt" and row["repair_matches_reference"] is True
    assert row["agent_file_content"] == ref
    assert row["test_on_clean_source"] == "n/a"
    path = benchmark.save_results([row], "unit", tmp_path)
    header = next(csv.reader(open(path, encoding="utf-8")))
    for col in ("category", "router_category", "pre_ci_status", "pre_ci_run_id", "post_ci_status",
                "pre_ci_sha", "post_ci_sha", "reference_file", "repair_matches_reference", "agent_file_content"):
        assert col in header


def test_failing_state_misrouted_config_row(repo_cwd, monkeypatch):
    """conf_001 routed to dependency: requirements.txt is edited, ci.yml stays broken."""
    e = BY_ID["conf_001"]
    _install(monkeypatch)
    monkeypatch.setattr(benchmark, "run_single_error",
                        _agent("dependency", ("requirements.txt", benchmark.ORIGINAL_REQUIREMENTS + "x==1\n")))
    row = benchmark.run_case_protocol_b(MODEL, e, True, False, 60, 60)
    assert json.loads(row["injected_files"]) == [CI_YML]
    assert row["agent_modified_file"] == "requirements.txt" and row["agent_file_is_injected"] is False
    assert row["reference_file"] == CI_YML and row["repair_matches_reference"] is False


def test_failing_state_green_precheck_and_excluded_are_skipped(repo_cwd, monkeypatch):
    called = []
    _install(monkeypatch, precheck="green")
    monkeypatch.setattr(benchmark, "run_single_error", lambda *a: called.append(a))
    row = benchmark.run_case_protocol_b(MODEL, BY_ID["dep_048"], True, False, 60, 60)
    assert called == [] and row["final_status"] == "precheck_green" and row["valid_case"] == 0
    row = benchmark.run_case_protocol_b(MODEL, BY_ID["conf_047"], True, False, 60, 60)
    assert row["final_status"] == "excluded" and "ruleset" in row["exclusion_reason"]
    row = benchmark.run_case_protocol_b(MODEL, NOOP_CONFIG, True, False, 60, 60)
    assert called == [] and row["final_status"] == "injection_failed"
