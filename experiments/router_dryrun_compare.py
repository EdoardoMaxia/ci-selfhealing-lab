"""
Compare Router results across conditions (MSR 2027 reviewer response, Q2). No LLM calls.

Conditions (per model, 150 cases):
  original   September paper run, no-memory CSV (Italian Router prompt, "<id>_benchmark" SHA)
  legacy_id  dry-run: "<id>_benchmark" SHA, current prompts/dataset      (control)
  opaque_id  dry-run: sha1(case_id) SHA, current prompts/dataset
  no_jobname dry-run: opaque_id + ci_job_name blanked

Tables:
  1  macro-F1 in the three main conditions + McNemar (legacy_id vs opaque_id)
  2  factor decomposition: original -> legacy_id (everything but the SHA), legacy_id -> opaque_id (SHA only)
  3  no_jobname vs opaque_id

Usage (repo root):
  python experiments/router_dryrun_compare.py [--results-dir experiments/results] [--markdown]
"""
import argparse
import csv
import glob
import math
from pathlib import Path

MODELS = ["ollama_qwen38_27b", "anthropic_haiku", "openai_gpt4o",
          "ollama_qwen3coder_30b", "ollama_llama8b", "ollama_mistral7b"]
LABELS = ["dependency", "test", "config"]


def macro_f1(true, pred):
    s = 0.0
    for c in LABELS:
        tp = sum(t == c and p == c for t, p in zip(true, pred))
        fp = sum(t != c and p == c for t, p in zip(true, pred))
        fn = sum(t == c and p != c for t, p in zip(true, pred))
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        s += 2 * pr * rc / (pr + rc) if pr + rc else 0.0
    return 100 * s / len(LABELS)


def mcnemar(a, b):
    """a, b: {case_id: correct(bool)}. Returns (only_a_correct, only_b_correct, exact two-sided p)."""
    ids = sorted(a)
    x = sum(a[i] and not b[i] for i in ids)
    y = sum(b[i] and not a[i] for i in ids)
    n = x + y
    p = min(1.0, 2 * sum(math.comb(n, k) for k in range(min(x, y) + 1)) / 2 ** n) if n else 1.0
    return x, y, p


def load_original(rdir, mid):
    files = sorted(glob.glob(str(rdir / f"benchmark_*_{mid}_nomemory.csv")))
    if not files:
        return None, None
    rows = list(csv.DictReader(open(files[-1], encoding="utf-8")))
    return {r["error_id"]: (r["category"], r["router_category"]) for r in rows}, Path(files[-1]).name


def load_dry(rdir, cond, mid):
    f = rdir / "router_dryrun" / f"router_dryrun_{cond}__{mid}.csv"
    if not f.exists():
        return None
    return {r["case_id"]: (r["true_category"], r["predicted_category"]) for r in csv.DictReader(open(f, encoding="utf-8"))}


def f1_of(d):
    ids = sorted(d)
    return macro_f1([d[i][0] for i in ids], [d[i][1] for i in ids])


def correct(d):
    return {i: t == p for i, (t, p) in d.items()}


def fmt(x, nd=2):
    return "n/a" if x is None else f"{x:.{nd}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", default="experiments/results")
    ap.add_argument("--markdown", action="store_true", help="print GitHub-style tables")
    args = ap.parse_args()
    rdir = Path(args.results_dir)

    data = {}
    for m in MODELS:
        orig, fname = load_original(rdir, m)
        data[m] = {"original": orig, "legacy_id": load_dry(rdir, "legacy_id", m),
                   "opaque_id": load_dry(rdir, "opaque_id", m), "no_jobname": load_dry(rdir, "no_jobname", m)}
        for k, v in data[m].items():
            if v is not None and len(v) != 150:
                print(f"WARNING {m}/{k}: {len(v)} cases (expected 150)")
        if fname:
            print(f"[{m}] original = {fname}")

    def table(title, header, rows):
        print(f"\n{title}")
        if args.markdown:
            print("| " + " | ".join(header) + " |\n|" + "---|" * len(header))
            for r in rows:
                print("| " + " | ".join(r) + " |")
        else:
            print("  ".join(f"{h:<18}" for h in header))
            for r in rows:
                print("  ".join(f"{c:<18}" for c in r))

    t1, t2, t3 = [], [], []
    for m in MODELS:
        d = data[m]
        fo = f1_of(d["original"]) if d["original"] else None
        fl = f1_of(d["legacy_id"]) if d["legacy_id"] else None
        fp = f1_of(d["opaque_id"]) if d["opaque_id"] else None
        fn = f1_of(d["no_jobname"]) if d["no_jobname"] else None
        if d["legacy_id"] and d["opaque_id"]:
            x, y, p = mcnemar(correct(d["legacy_id"]), correct(d["opaque_id"]))
            dl = f"{fp - fl:+.2f}"
            mc, pv = f"{x}/{y}", f"{p:.2f}"
        else:
            dl, mc, pv = "n/a", "n/a", "n/a"
        t1.append([m, fmt(fo), fmt(fl), fmt(fp), dl, mc, pv])
        d_lang = f"{fl - fo:+.2f}" if fl is not None and fo is not None else "n/a"
        d_leak = f"{fp - fl:+.2f}" if fp is not None and fl is not None else "n/a"
        d_tot = f"{fp - fo:+.2f}" if fp is not None and fo is not None else "n/a"
        t2.append([m, d_lang, d_leak, d_tot])
        if d["no_jobname"] and d["opaque_id"]:
            x, y, p = mcnemar(correct(d["opaque_id"]), correct(d["no_jobname"]))
            t3.append([m, fmt(fp), fmt(fn), f"{fn - fp:+.2f}", f"{x}/{y}", f"{p:.2f}"])
        else:
            t3.append([m, fmt(fp), fmt(fn), "n/a", "n/a", "n/a"])

    table("Table 1 - macro-F1 in three conditions (McNemar: legacy_id vs opaque_id; cols = only-legacy-correct/only-opaque-correct, exact two-sided p)",
          ["model", "F1 original", "F1 legacy_id", "F1 opaque_id", "d opaque-legacy", "discordant", "McNemar p"], t1)
    table("Table 2 - factor decomposition (F1 points)",
          ["model", "language+rest (orig->legacy)", "leakage (legacy->opaque)", "total (orig->opaque)"], t2)
    table("Table 3 - no_jobname vs opaque_id (discordant = only-with-jobname-correct/only-without-correct)",
          ["model", "F1 opaque_id", "F1 no_jobname", "delta", "discordant", "McNemar p"], t3)
    print("\nNote: 'original -> legacy_id' bundles every change except the SHA (Router prompt language, dataset/log language, "
          "and any other code/library drift); it is not a pure language effect.")


if __name__ == "__main__":
    main()
