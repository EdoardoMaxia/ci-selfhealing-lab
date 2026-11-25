"""
F2 rerun summary (MSR 2027 revision): Success Rate per model and category in the two arms,
skipped cases by reason (expected 0), duration. Markdown on stdout. No LLM, no network.

Arms (files written by experiments/run_f2_rerun.sh, --failing-state):
  baseline  benchmark_*_nomemory_failstate.csv  dependency + config (39 cases);
            the "test" baseline comes from A2 (--a2-dir: benchmark_*_nomemory_protob.csv, 39 cases)
  memory    benchmark_*_memory_failstate.csv    all 78 cases (Haiku = calibration run)

Only the cases NOT in experiments/excluded_cases.json count. A case counts as valid when its
row has valid_case = 1 (red pre-check, agent run); an included case that is skipped (not red
pre-check, not injectable) or missing is reported under "skipped by reason". Timeouts and
errors after a red pre-check are failures, reported separately.

Usage:
  python experiments/f2_rerun_summary.py --dir experiments/results/f2_rerun \
      --a2-dir experiments/results/a2_test_rerun --steps experiments/results/f2_rerun/steps.tsv
"""
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.benchmark import EXCLUDED_CASES  # noqa: E402
from experiments.dataset import DATASET           # noqa: E402

CATEGORIES = ("dependency", "config", "test")
MODEL_ORDER = ["anthropic_haiku", "openai_gpt4o", "ollama_qwen38_27b",
               "ollama_qwen3coder_30b", "ollama_llama8b", "ollama_mistral7b"]
FILE_RE = re.compile(r"benchmark_(\d{8}_\d{6})_(.+)_(nomemory|memory)_(failstate|protob)\.csv$")


def included_cases():
    return {e["id"]: e["category"] for e in DATASET if e["id"] not in EXCLUDED_CASES}


def load_rows(directory: Path, suffix: str):
    """{(arm, model_id): {case_id: row}}; a later file overrides an earlier one for the same case."""
    out = defaultdict(dict)
    files = []
    for path in sorted(directory.glob("benchmark_*.csv")):
        m = FILE_RE.match(path.name)
        if not m or m.group(4) != suffix or m.group(2) == "all_models":
            continue
        files.append(path.name)
        arm = "baseline" if m.group(3) == "nomemory" else "memory"
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                out[(arm, row["model_id"])][row["error_id"]] = row
    return out, files


def is_valid(row) -> bool:
    return str(row.get("valid_case", "")).strip() in ("1", "True", "true")


def is_success(row) -> bool:
    return str(row.get("success", "")).strip() in ("1", "True", "true")


def mcnemar_p(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(comb(n, k) for k in range(min(b, c) + 1)) / 2 ** n)


def summarize(f2_dir: Path, a2_dir: Path = None, steps: Path = None) -> str:
    cases = included_cases()
    expected = {"baseline": {c for c, cat in cases.items() if cat != "test"}, "memory": set(cases)}
    f2, f2_files = load_rows(f2_dir, "failstate")
    a2, a2_files = (load_rows(a2_dir, "protob") if a2_dir and a2_dir.is_dir() else ({}, []))

    # merged[arm][model][case] -> row; A2 provides the baseline test rows
    merged = defaultdict(lambda: defaultdict(dict))
    for (arm, model), rows in f2.items():
        for cid, row in rows.items():
            if cid in expected[arm]:
                merged[arm][model][cid] = row
    for (arm, model), rows in a2.items():
        if arm != "baseline":
            continue
        for cid, row in rows.items():
            if cases.get(cid) == "test":
                merged["baseline"][model][cid] = row
    models = [m for m in MODEL_ORDER if any(m in merged[a] for a in merged)] + \
             sorted({m for a in merged for m in merged[a]} - set(MODEL_ORDER))

    n_cat = Counter(cases.values())
    lines = ["# F2 rerun — corrected benchmark (78 cases, --failing-state)", ""]
    lines.append(f"Included cases: {len(cases)} (" + ", ".join(f"{c} {n_cat[c]}" for c in CATEGORIES)
                 + f"); excluded: {len(EXCLUDED_CASES)} (experiments/excluded_cases.json).")
    lines.append(f"F2 files: {len(f2_files)}; A2 files (test baseline): {len(a2_files)}"
                 + ("" if a2_files else " — **missing: the baseline lacks the test category**") + ".")
    lines.append("")

    skipped_rows, timeouts = [], []
    sr = {}
    for arm in ("baseline", "memory"):
        title = ("Baseline, no memory (dependency + config: F2; test: A2)" if arm == "baseline"
                 else "Memory arm (Haiku = calibration, others read-only)")
        lines += [f"## {title}", "",
                  "| Model | dependency | config | test | **total** | SR % | router acc. % |",
                  "|---|---|---|---|---|---|---|"]
        for model in models:
            rows = merged[arm].get(model, {})
            cells, tot_ok, tot_valid, rc, rv = [], 0, 0, 0, 0
            for cat in CATEGORIES:
                want = [c for c, k in cases.items() if k == cat]
                valid = [rows[c] for c in want if c in rows and is_valid(rows[c])]
                ok = sum(is_success(r) for r in valid)
                cells.append(f"{ok}/{len(valid)}" if valid else "—")
                tot_ok += ok; tot_valid += len(valid)
                rc += sum(str(r.get("router_correct")) in ("1", "True") for r in valid); rv += len(valid)
                for c in want:
                    if cat == "test" and arm == "baseline":
                        src = "A2"
                    else:
                        src = "F2"
                    if c not in rows:
                        if not (cat == "test" and arm == "baseline" and not a2_files):
                            skipped_rows.append((arm, model, c, "missing (no row)", src))
                    elif not is_valid(rows[c]):
                        skipped_rows.append((arm, model, c, rows[c].get("final_status", "?"), src))
                    elif rows[c].get("final_status") in ("timeout", "error"):
                        timeouts.append((arm, model, c, rows[c].get("final_status"), rows[c].get("error_msg", "")[:80]))
            sr[(arm, model)] = {c: is_success(r) for c, r in rows.items() if is_valid(r)}
            pct = f"{100 * tot_ok / tot_valid:.1f}" if tot_valid else "—"
            racc = f"{100 * rc / rv:.1f}" if rv else "—"
            lines.append(f"| {model} | " + " | ".join(cells) + f" | **{tot_ok}/{tot_valid}** | {pct} | {racc} |")
        lines.append("")

    lines += ["## Memory effect (paired valid cases)", "",
              "| Model | n paired | no-mem SR % | mem SR % | Δ pp | b (gained) | c (lost) | McNemar p |",
              "|---|---|---|---|---|---|---|---|"]
    for model in models:
        base, mem = sr.get(("baseline", model), {}), sr.get(("memory", model), {})
        paired = sorted(set(base) & set(mem))
        if not paired:
            continue
        b = sum(1 for c in paired if not base[c] and mem[c])
        c_ = sum(1 for c in paired if base[c] and not mem[c])
        s0 = 100 * sum(base[c] for c in paired) / len(paired)
        s1 = 100 * sum(mem[c] for c in paired) / len(paired)
        lines.append(f"| {model} | {len(paired)} | {s0:.1f} | {s1:.1f} | {s1 - s0:+.2f} | {b} | {c_} | {mcnemar_p(b, c_):.3f} |")
    lines.append("")

    lines += ["## Skipped included cases, by reason (expected: none)", ""]
    if skipped_rows:
        by_reason = Counter(r[3] for r in skipped_rows)
        lines.append("Totals: " + ", ".join(f"{k} = {v}" for k, v in sorted(by_reason.items())))
        lines += ["", "| Arm | Model | Case | Reason | Source |", "|---|---|---|---|---|"]
        lines += [f"| {a} | {m} | {c} | {r} | {s} |" for a, m, c, r, s in skipped_rows]
    else:
        lines.append("None: every included case had a red pre-check and was run.")
    lines.append("")
    lines += ["## Timeouts / errors after a red pre-check (counted as failures)", ""]
    if timeouts:
        lines += ["| Arm | Model | Case | Status | Message |", "|---|---|---|---|---|"]
        lines += [f"| {a} | {m} | {c} | {s} | {msg} |" for a, m, c, s, msg in timeouts]
    else:
        lines.append("None.")
    lines.append("")

    if steps and steps.is_file():
        rows = [l.rstrip("\n").split("\t") for l in steps.read_text(encoding="utf-8").splitlines() if l.strip()]
        lines += ["## Duration", "", "| Step | start | minutes | exit |", "|---|---|---|---|"]
        for name, t0, t1, rc in rows:
            lines.append(f"| {name} | {datetime.fromtimestamp(int(t0)):%d/%m %H:%M} | {(int(t1) - int(t0)) / 60:.0f} | {rc} |")
        if rows:
            first, last = min(int(r[1]) for r in rows), max(int(r[2]) for r in rows)
            busy = sum(int(r[2]) - int(r[1]) for r in rows)
            lines += ["", f"Wall clock: {(last - first) / 3600:.1f} h "
                          f"({datetime.fromtimestamp(first):%d/%m %H:%M} → {datetime.fromtimestamp(last):%d/%m %H:%M}); "
                          f"sum of the steps: {busy / 3600:.1f} h."]
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--dir", type=Path, default=ROOT / "experiments" / "results" / "f2_rerun")
    ap.add_argument("--a2-dir", type=Path, default=ROOT / "experiments" / "results" / "a2_test_rerun")
    ap.add_argument("--steps", type=Path, default=None)
    args = ap.parse_args()
    print(summarize(args.dir, args.a2_dir, args.steps or args.dir / "steps.tsv"))


if __name__ == "__main__":
    main()
