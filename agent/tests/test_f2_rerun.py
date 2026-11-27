"""
F2 rerun (MSR revision): unattended runner and summary.

Deterministic: no LLM, no GitHub, no Ollama. The runner is exercised in DRY_RUN mode on a
copy placed in a temporary directory (it writes nothing into the repository).

Run:  python -m pytest agent/tests/test_f2_rerun.py -v
"""
import csv
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from experiments import f2_rerun_summary as summary
from experiments.benchmark import EXCLUDED_CASES
from experiments.dataset import DATASET

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "experiments" / "run_f2_rerun.sh"
INCLUDED = {e["id"]: e["category"] for e in DATASET if e["id"] not in EXCLUDED_CASES}


def _dry_run(tmp_path):
    (tmp_path / "experiments").mkdir()
    shutil.copy(SCRIPT, tmp_path / "experiments" / "run_f2_rerun.sh")
    proc = subprocess.run(["bash", "experiments/run_f2_rerun.sh"], cwd=tmp_path, capture_output=True,
                          text=True, timeout=60, env={**os.environ, "DRY_RUN": "1"})
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return [l.split(" :: ", 1) for l in proc.stdout.splitlines() if " START " in l]


def test_runner_script_is_executable_and_parses():
    assert os.access(SCRIPT, os.X_OK)
    assert subprocess.run(["bash", "-n", str(SCRIPT)]).returncode == 0
    text = SCRIPT.read_text()
    assert "main \"$@\"" in text and "code_fingerprint" in text and "episodic_memory_pre_f2_" in text


def test_runner_dry_run_steps(tmp_path):
    steps = _dry_run(tmp_path)
    names = [s[0].split("START ")[1] for s in steps]
    cmds = {s[0].split("START ")[1]: s[1] for s in steps}
    base = [n for n in names if n.startswith("base_")]
    ro = [n for n in names if n.startswith("ro_")]
    assert len(base) == 12 and len(ro) == 5 and names.count("calib_haiku") == 1
    assert names.index("calib_haiku") > max(names.index(n) for n in base)       # baselines first
    assert names.index("calib_haiku") < min(names.index(n) for n in ro)         # read-only last
    for n in base:   # 6 models x (dependency, config), no memory, never the test category
        assert "--failing-state" in cmds[n] and "--no-memory" in cmds[n]
        assert ("--category dependency" in cmds[n]) != ("--category config" in cmds[n])
    assert "--clean-memory" in cmds["base_haiku_dependency"]
    calib = cmds["calib_haiku"]
    assert "--provider anthropic" in calib and "--failing-state" in calib and "--clean-memory" in calib
    assert "--no-memory" not in calib and "--readonly-memory" not in calib and "--category" not in calib
    for n in ro:     # the other 5 models, all 78 cases, read-only
        assert "--failing-state" in cmds[n] and "--readonly-memory" in cmds[n] and "--category" not in cmds[n]
        assert "anthropic" not in cmds[n] and "--clean-memory" not in cmds[n]
    assert not any("--test-protocol-b" in c for c in cmds.values())
    assert (tmp_path / "experiments" / "results" / "f2_rerun" / ".date").is_file()   # written in the copy only


# ── summary ───────────────────────────────────────────────────

FIELDS = ["model_id", "model_name", "error_id", "category", "final_status", "success", "valid_case",
          "router_correct", "error_msg"]


def _write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)


def _row(model, cid, success, valid=1, status=None):
    return {"model_id": model, "model_name": model, "error_id": cid, "category": INCLUDED.get(cid, "config"),
            "final_status": status or ("fixed" if success else "escalated"), "success": int(success),
            "valid_case": valid, "router_correct": 1, "error_msg": ""}


def test_summary_counts_and_skips(tmp_path):
    f2, a2 = tmp_path / "f2", tmp_path / "a2"; f2.mkdir(); a2.mkdir()
    m = "anthropic_haiku"
    dep = [c for c, k in INCLUDED.items() if k == "dependency"]
    conf = [c for c, k in INCLUDED.items() if k == "config"]
    test = [c for c, k in INCLUDED.items() if k == "test"]
    assert (len(dep), len(conf), len(test)) == (35, 4, 39)
    # baseline: dependency all fixed but one skipped (green pre-check); config file lacks conf_013
    _write(f2 / f"benchmark_20261126_100000_{m}_nomemory_failstate.csv",
           [_row(m, c, True) for c in dep[:-1]] + [_row(m, dep[-1], False, valid=0, status="precheck_green")]
           + [_row(m, "conf_031", False, valid=0, status="excluded")])
    _write(f2 / f"benchmark_20261126_110000_{m}_nomemory_failstate.csv",
           [_row(m, c, c != "conf_001") for c in conf if c != "conf_013"])
    _write(a2 / f"benchmark_20261119_100000_{m}_nomemory_protob.csv", [_row(m, c, i % 2 == 0) for i, c in enumerate(test)])
    # memory arm: everything fixed, one timeout
    mem = [_row(m, c, True) for c in INCLUDED]
    mem[0] = _row(m, mem[0]["error_id"], False, status="timeout")
    _write(f2 / f"benchmark_20261127_100000_{m}_memory_failstate.csv", mem)
    (f2 / "steps.tsv").write_text("base_haiku_dependency\t1764150000\t1764153600\t0\n", encoding="utf-8")

    out = summary.summarize(f2, a2, f2 / "steps.tsv")
    base_line = next(l for l in out.splitlines() if l.startswith(f"| {m} |"))
    assert "| 34/34 | 2/3 | 20/39 | **56/76** |" in base_line           # conf_013 missing, dep_x skipped
    assert "precheck_green = 1" in out and "missing (no row) = 1" in out
    assert "conf_031" not in out                                         # excluded cases never count
    assert "| timeout |" in out
    assert "Wall clock: 1.0 h" in out
    paired = next(l for l in out.splitlines() if l.startswith(f"| {m} | 76 |"))
    cols = [x.strip() for x in paired.split("|")]
    assert (cols[6], cols[7]) == ("20", "1")        # b: 19 test + conf_001 gained; c: dep_001 lost (timeout)
    assert summary.mcnemar_p(20, 1) == pytest.approx(22 / 2 ** 21 * 2)


def test_corrections_file_is_well_formed():
    path = REPO_ROOT / "experiments" / "f2_corrections.json"
    items = summary.load_corrections(path)
    assert {(c["model_id"], c["case_id"], c["action"]) for c in items} == {
        ("openai_gpt4o", "dep_002", "success"), ("ollama_qwen3coder_30b", "dep_042", "drop")}
    for c in items:
        assert c["case_id"] in INCLUDED and c["model_id"] in summary.MODEL_ORDER
        assert c["reason"] and c["evidence"].get("log", "").startswith("experiments/results/f2_rerun/logs/")


def test_corrections_success_and_drop(tmp_path):
    f2 = tmp_path / "f2"; f2.mkdir()
    m = "openai_gpt4o"
    dep = [c for c, k in INCLUDED.items() if k == "dependency"]
    base = [_row(m, c, True) for c in dep]
    base[1] = _row(m, dep[1], False, status="error")          # harness error after a green CI
    base[2] = _row(m, dep[2], False, status="error")          # harness error, outcome unknown
    _write(f2 / f"benchmark_20261126_100000_{m}_nomemory_failstate.csv", base)
    mem = [_row(m, c, True) for c in dep]
    mem[2] = _row(m, dep[2], False)
    _write(f2 / f"benchmark_20261127_100000_{m}_memory_failstate.csv", mem)
    corr = tmp_path / "corr.json"
    corr.write_text(json.dumps({"corrections": [
        {"arm": "baseline", "model_id": m, "case_id": dep[1], "action": "success", "reason": "r1", "evidence": {}},
        {"arm": "both", "model_id": m, "case_id": dep[2], "action": "drop", "reason": "r2", "evidence": {}}]}))

    raw = summary.summarize(f2, None, None, None)
    out = summary.summarize(f2, None, None, corr)
    assert f"| {m} | 34/35 |" in raw and f"| {m} | 35/35 |" not in raw
    base_line = next(l for l in out.splitlines() if l.startswith(f"| {m} |"))
    assert base_line.startswith(f"| {m} | 34/34 |")            # dep[1] corrected, dep[2] dropped
    paired = next(l for l in out.splitlines() if l.startswith(f"| {m} | 34 |"))
    cols = [x.strip() for x in paired.split("|")]
    assert (cols[6], cols[7]) == ("0", "0")                    # no spurious gain left
    assert "Corrections applied" in out and "r1" in out and "r2" in out
    assert "| error |" not in out.split("## Timeouts")[1]
    skipped = out.split("## Skipped")[1].split("## Timeouts")[0]
    assert f"| {dep[2]} |" not in skipped and f"| {dep[1]} |" not in skipped   # dropped/corrected: not "missing"

    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"corrections": [
        {"arm": "memory", "model_id": m, "case_id": "dep_999", "action": "success", "reason": "x", "evidence": {}}]}))
    with pytest.raises(SystemExit):
        summary.summarize(f2, None, None, bad)
