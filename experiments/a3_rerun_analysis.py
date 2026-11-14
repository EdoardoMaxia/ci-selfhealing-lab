"""
A3 memory-ablation rerun: old (September, paper) vs new (corrected code) results.
No LLM calls; reads the benchmark CSVs only (columns: model_id, error_id, category, success,
fix_attempt, memory_hits, memory_active, ...).

  --old-dir  experiments/results            September files: benchmark_2026090*/0910*_<model>_(no)memory.csv
  --new-dir  experiments/results/a3_rerun   rerun files, same naming (benchmark_<ts>_<model>_(no)memory.csv)
For every (model, condition) the LATEST file in each dir is used and printed, so keep only the
runs you mean to analyse in --new-dir (e.g. do not leave the Haiku calibration run next to a
separate Haiku read-only run unless you want the later one).

Tables: 1 SR with/without memory (old/new), 2 SR per category, 3 attempt distribution (memory),
4 cases that received episodes (memory_hits>0) and their outcome, 5 per-case gained/lost vs no-memory.
Usage: python experiments/a3_rerun_analysis.py --new-dir experiments/results/a3_rerun [--markdown]
"""
import argparse
import csv
import glob
from pathlib import Path

MODELS = ["anthropic_haiku", "openai_gpt4o", "ollama_qwen38_27b",
          "ollama_qwen3coder_30b", "ollama_llama8b", "ollama_mistral7b"]
CATS = ["dependency", "test", "config"]


def load(d, model, cond, tag):
    files = sorted(glob.glob(str(Path(d) / f"benchmark_*_{model}_{cond}.csv")))
    if cond == "memory":                       # "memory" must not match "nomemory"
        files = [f for f in files if not f.endswith("_nomemory.csv")]
    if not files:
        return None
    print(f"[{tag}] {model}/{cond}: {Path(files[-1]).name}")
    rows = list(csv.DictReader(open(files[-1], encoding="utf-8")))
    return {r["error_id"]: r for r in rows}


def ok(r):
    return str(r["success"]).strip().lower() in ("1", "true", "1.0")


def sr(d, cat=None):
    if not d:
        return None
    rs = [r for r in d.values() if cat is None or r["category"] == cat]
    return 100 * sum(ok(r) for r in rs) / len(rs) if rs else None


def f(x, nd=2):
    return "n/a" if x is None else f"{x:.{nd}f}"


def dl(a, b):
    return "n/a" if a is None or b is None else f"{b - a:+.2f}"


def show(title, header, rows, md):
    print(f"\n{title}")
    if md:
        print("| " + " | ".join(header) + " |\n|" + "---|" * len(header))
        for r in rows:
            print("| " + " | ".join(r) + " |")
    else:
        for r in [header] + rows:
            print("  ".join(f"{c:<16}" for c in r))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-dir", default="experiments/results")
    ap.add_argument("--new-dir", default="experiments/results/a3_rerun")
    ap.add_argument("--markdown", action="store_true")
    a = ap.parse_args()
    D = {m: {"on": load(a.old_dir, m, "nomemory", "old"), "om": load(a.old_dir, m, "memory", "old"),
             "nn": load(a.new_dir, m, "nomemory", "new"), "nm": load(a.new_dir, m, "memory", "new")} for m in MODELS}

    t1, t2, t3, t4, t5 = [], [], [], [], []
    for m in MODELS:
        d = D[m]
        t1.append([m, f(sr(d["on"])), f(sr(d["nn"])), f(sr(d["om"])), f(sr(d["nm"])),
                   dl(sr(d["on"]), sr(d["om"])), dl(sr(d["nn"]), sr(d["nm"]))])
        t2.append([m] + [f(sr(d[k], c)) for c in CATS for k in ("nn", "nm")])
        if d["nm"]:
            rs = list(d["nm"].values())
            n = len(rs)
            att = lambda k: sum(ok(r) and str(r["fix_attempt"]).split(".")[0] == str(k) for r in rs)
            t3.append([m, f"{att(1)}", f"{att(2)}", f"{att(3)}", f"{sum(not ok(r) for r in rs)}", f"{n}"])
        else:
            t3.append([m, "n/a", "n/a", "n/a", "n/a", "n/a"])
        for tag, k in (("old", "om"), ("new", "nm")):
            if d[k]:
                hit = [r for r in d[k].values() if float(r.get("memory_hits") or 0) > 0]
                t4.append([m, tag, str(len(hit)), str(sum(ok(r) for r in hit)), str(sum(not ok(r) for r in hit))])
            else:
                t4.append([m, tag, "n/a", "n/a", "n/a"])
        if d["nn"] and d["nm"]:
            ids = sorted(set(d["nn"]) & set(d["nm"]))
            g = sum(ok(d["nm"][i]) and not ok(d["nn"][i]) for i in ids)
            l = sum(ok(d["nn"][i]) and not ok(d["nm"][i]) for i in ids)
            t5.append([m, f(sr(d["nn"])), f(sr(d["nm"])), dl(sr(d["nn"]), sr(d["nm"])), str(g), str(l)])
        else:
            t5.append([m, "n/a", "n/a", "n/a", "n/a", "n/a"])

    show("Table 1 - SR % with/without memory (old = paper/September, new = rerun)",
         ["model", "SR nomem old", "SR nomem new", "SR mem old", "SR mem new", "d mem old", "d mem new"], t1, a.markdown)
    show("Table 2 - SR % per category (new run)",
         ["model"] + [f"{c[:4]} {k}" for c in CATS for k in ("nomem", "mem")], t2, a.markdown)
    show("Table 3 - successes by attempt, new memory run (fix_attempt = attempt of the successful fix; check the column semantics)",
         ["model", "T1", "T2", "T3", "failed", "n"], t3, a.markdown)
    show("Table 4 - cases that received episodes (memory_hits>0)",
         ["model", "run", "cases w/ episodes", "solved", "failed"], t4, a.markdown)
    show("Table 5 - cross-model transfer (new): memory vs no-memory per case",
         ["model", "SR nomem", "SR mem", "delta", "gained", "lost"], t5, a.markdown)


if __name__ == "__main__":
    main()
