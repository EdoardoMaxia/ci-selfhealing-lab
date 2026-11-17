"""
Summary of the A2 rerun (protocol B, "test" category) — markdown on stdout.

Reads, in --dir (default experiments/results/a2_test_rerun):
  benchmark_<ts>_<model_id>_<memory>_protob.csv   one per model (latest file per model wins)
  verify_excluded_<ts>.csv                         latest file

Usage:
    python experiments/a2_test_rerun_summary.py > experiments/results/a2_test_rerun/a2_test_rerun_summary.md
"""
import re
import csv
import json
import argparse
from pathlib import Path

MODEL_ORDER = ["anthropic_haiku", "openai_gpt4o", "ollama_qwen38_27b",
               "ollama_qwen3coder_30b", "ollama_llama8b", "ollama_mistral7b"]


def load(dir_: Path):
    latest = {}
    for p in sorted(dir_.glob("benchmark_*_protob.csv")):
        rows = list(csv.DictReader(open(p, encoding="utf-8")))
        ids = {r["model_id"] for r in rows}
        if len(ids) != 1:               # all_models aggregate: per-model files are enough
            continue
        latest[ids.pop()] = (p.name, rows)   # sorted by timestamp: the last one wins
    order = [m for m in MODEL_ORDER if m in latest] + sorted(set(latest) - set(MODEL_ORDER))
    verify = sorted(dir_.glob("verify_excluded_*.csv"))
    vrows = list(csv.DictReader(open(verify[-1], encoding="utf-8"))) if verify else []
    return [(m, *latest[m]) for m in order], (verify[-1].name if verify else None), vrows


def pct(a, b):
    return f"{a / b * 100:.1f}" if b else "n/a"


def truthy(v):
    return str(v).strip().lower() in ("1", "true")


def kmr(v):
    m = re.fullmatch(r"(\d+)/(\d+)/(\d+)", v or "")
    return tuple(map(int, m.groups())) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="experiments/results/a2_test_rerun")
    args = ap.parse_args()
    models, vname, vrows = load(Path(args.dir))
    out = []
    w = out.append

    w("# A2 — rerun of the \"test\" category with protocol B\n")
    w("Protocol B: only test files may be modified; the 11 cases whose error is injected "
      "outside the test file are excluded; the CI must be RED on the full failed state "
      "(pre-check) before the agent runs; every fix branch starts from that state; "
      "SR = fixed / valid cases (pre-check red).\n")
    w("Files: " + ", ".join(f"`{f}`" for _, f, _ in models) + "\n")

    # 1. accounting + SR
    w("## 1. Cases and Success Rate\n")
    w("| Model | rows | excluded | inj. failed | pre red | pre green | pre error | valid | fixed | escalated | timeout/error | **SR %** | Router acc. % |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    pooled = {"valid": 0, "fixed": 0}
    anomalies = []
    for mid, _, rows in models:
        valid = [r for r in rows if truthy(r["valid_case"])]
        fixed = [r for r in valid if truthy(r["success"])]
        esc   = [r for r in valid if r["final_status"] == "escalated"]
        other = [r for r in valid if r["final_status"] in ("timeout", "error")]
        c = lambda k, v: sum(1 for r in rows if r[k] == v)
        pooled["valid"] += len(valid); pooled["fixed"] += len(fixed)
        anomalies += [(mid, r["error_id"], r["pre_ci_status"], r["pre_ci_run_id"], r["error_msg"])
                      for r in rows if r["final_status"] in ("precheck_green", "precheck_error", "injection_failed")]
        w(f"| {rows[0]['model_name']} | {len(rows)} | {sum(truthy(r['excluded']) for r in rows)} | "
          f"{c('final_status', 'injection_failed')} | {c('pre_ci_status', 'red')} | {c('pre_ci_status', 'green')} | "
          f"{c('pre_ci_status', 'error')} | {len(valid)} | {len(fixed)} | {len(esc)} | {len(other)} | "
          f"**{pct(len(fixed), len(valid))}** | {pct(sum(truthy(r['router_correct']) for r in valid), len(valid))} |")
    w(f"| **Pooled** | | | | | | | {pooled['valid']} | {pooled['fixed']} | | | "
      f"**{pct(pooled['fixed'], pooled['valid'])}** | |\n")

    # 2. attempts
    w("## 2. Attempt at which the fix succeeded (fixed cases)\n")
    w("| Model | T1 | T2 | T3 | escalated |")
    w("|---|---|---|---|---|")
    for mid, _, rows in models:
        valid = [r for r in rows if truthy(r["valid_case"])]
        att = lambda n: sum(1 for r in valid if truthy(r["success"]) and r["fix_attempt"] in (str(n), f"{n}.0"))
        w(f"| {rows[0]['model_name']} | {att(1)} | {att(2)} | {att(3)} | "
          f"{sum(1 for r in valid if r['final_status'] == 'escalated')} |")
    w("")

    # 3. quality of the fixes
    w("## 3. Fixed cases: CI vs clean source vs assertions\n")
    w("Assertions are compared with the ORIGINAL test (clean baseline before the injection): "
      "k/m/r = kept / modified / removed. A fixed case with m>0 or r>0 changed what the test checks.\n")
    w("| Model | fixed | post-CI green | clean source pass | clean source fail | agent file = injected file | all assertions kept | ≥1 modified | ≥1 removed | k/m/r total |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    flagged = []
    for mid, _, rows in models:
        fx = [r for r in rows if truthy(r["valid_case"]) and truthy(r["success"])]
        t = [kmr(r["assertions_preserved"]) for r in fx]
        tk = [x for x in t if x]
        for r in fx:
            x = kmr(r["assertions_preserved"])
            if r["test_on_clean_source"] != "pass" or not x or x[1] or x[2]:
                flagged.append((mid, r["error_id"], r["test_on_clean_source"], r["assertions_preserved"]))
        w(f"| {rows[0]['model_name']} | {len(fx)} | {sum(r['post_ci_status'] == 'green' for r in fx)} | "
          f"{sum(r['test_on_clean_source'] == 'pass' for r in fx)} | "
          f"{sum(r['test_on_clean_source'] == 'fail' for r in fx)} | "
          f"{sum(truthy(r['agent_file_is_injected']) for r in fx)} | "
          f"{sum(1 for x in tk if x[1] == 0 and x[2] == 0)} | {sum(1 for x in tk if x[1])} | "
          f"{sum(1 for x in tk if x[2])} | "
          f"{sum(x[0] for x in tk)}/{sum(x[1] for x in tk)}/{sum(x[2] for x in tk)} |")
    w("")
    if flagged:
        w("Fixed cases to inspect (clean source not passing, or assertions modified/removed):\n")
        w("| Model | Case | clean source | k/m/r |")
        w("|---|---|---|---|")
        for f in flagged:
            w(f"| {f[0]} | {f[1]} | {f[2]} | {f[3]} |")
        w("")

    # 4. anomalies
    w("## 4. Pre-check anomalies (cases skipped)\n")
    if anomalies:
        w("| Model | Case | pre-CI | run id | message |")
        w("|---|---|---|---|---|")
        for a in anomalies:
            w(f"| {a[0]} | {a[1]} | {a[2]} | {a[3]} | {a[4][:80]} |")
    else:
        w("None: the CI was red on the failed state for every valid case.")
    w("")

    # 5. per-case matrix
    if models:
        w("## 5. Per case (F<n> = fixed at attempt n, esc = escalated, — = not valid)\n")
        w("| Case | " + " | ".join(m for m, _, _ in models) + " |")
        w("|---|" + "---|" * len(models))
        cases = sorted({r["error_id"] for _, _, rows in models for r in rows})
        idx = {(m, r["error_id"]): r for m, _, rows in models for r in rows}
        for cid in cases:
            cells = []
            for m, _, _ in models:
                r = idx.get((m, cid))
                if not r or not truthy(r["valid_case"]):
                    cells.append("excl" if r and truthy(r["excluded"]) else "—")
                elif truthy(r["success"]):
                    cells.append(f"F{(r['fix_attempt'] or '?').split('.')[0]}")
                else:
                    cells.append("esc" if r["final_status"] == "escalated" else r["final_status"])
            w(f"| {cid} | " + " | ".join(cells) + " |")
        w("")

    # 6. verify-excluded
    w("## 6. The 11 excluded cases under the old protocol (`--verify-excluded`)\n")
    if vrows:
        w(f"File: `{vname}`. *test file only* = what the old Fix Executor committed "
          "(branch from clean main + test file); *full failed state* = injected file included.\n")
        w("| Case | error injected in | test file only | full failed state | bug confirmed | runs (only / full) |")
        w("|---|---|---|---|---|---|")
        for r in vrows:
            w(f"| {r['case_id']} | `{r['injected_target']}` | {r['testonly_ci_status'] or '-'} | "
              f"{r['fullstate_ci_status'] or '-'} | {'yes' if truthy(r['bug_confirmed']) else 'NO'} | "
              f"{r['testonly_run_id']} / {r['fullstate_run_id']} |")
        w(f"\nBug confirmed on {sum(truthy(r['bug_confirmed']) for r in vrows)}/{len(vrows)} cases.")
    else:
        w("No verify_excluded_*.csv found.")
    print("\n".join(out))


if __name__ == "__main__":
    main()
