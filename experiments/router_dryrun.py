"""
Router-only dry-run (Fix A1 follow-up, MSR 2027 reviewer response).

Calls ONLY the Router Agent (agent.agents.router.router_node): no specialist agent,
no fix, no CI, no memory. For each of the 150 dataset cases it builds the same input
state as experiments/benchmark.py (with the opaque SHA1 commit_sha) and records the
Router's prediction.

Conditions:
  opaque_id    commit_sha = sha1(case_id)                      (the fixed benchmark input)
  no_jobname   same, but ci_job_name removed (set to "")       (robustness check)
  legacy_id    commit_sha = "<case_id>_benchmark"              (CONTROL ONLY: the pre-fix format, whose
                                                                first 8 chars reveal the category prefix;
                                                                same prompts/dataset as opaque_id, so
                                                                legacy_id vs opaque_id isolates the leak)
  (--condition both = opaque_id + no_jobname; legacy_id must be requested explicitly)

Outputs (one pair per model, in experiments/results/router_dryrun/):
  router_dryrun_opaque_id__<model_id>.csv     case_id,true_category,predicted_category,confidence
  router_dryrun_no_jobname__<model_id>.csv
  router_dryrun_legacy_id__<model_id>.csv
  router_dryrun_summary.csv                   one row per (model, condition): accuracy, macro-F1, ...

Usage (from the repo root):
  python experiments/router_dryrun.py --list-models
  python experiments/router_dryrun.py --model-id anthropic_haiku
  python experiments/router_dryrun.py --model-id openai_gpt4o --condition no_jobname
  python experiments/router_dryrun.py --model-id openai_gpt4o --condition legacy_id
  python experiments/router_dryrun.py --model-id ollama_llama8b --limit 5      # smoke test
  python experiments/router_dryrun.py --all                                    # every model in MODELS
"""

import os
import sys
import csv
import time
import hashlib
import argparse
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.dataset import DATASET          # noqa: E402
from experiments.benchmark import MODELS         # noqa: E402  (single source of truth for the models)

OUT_DIR = Path(__file__).parent / "results" / "router_dryrun"
LABELS = ["dependency", "test", "config"]        # ground-truth classes; "unknown" is a valid (wrong) prediction
CONDITIONS = ("opaque_id", "no_jobname")          # run by --condition both
CONTROL_CONDITIONS = ("legacy_id",)                   # must be requested explicitly


# ──────────────────────────────────────────────────────────────
# State construction — must mirror benchmark.run_single_error
# ──────────────────────────────────────────────────────────────

def build_state(error: dict, condition: str) -> dict:
    if condition == "legacy_id":
        # Pre-fix format, kept ONLY as a control: "dep_001_benchmark"[:8] == "dep_001_".
        sha = f"{error['id']}_benchmark"
    else:
        sha = hashlib.sha1(error["id"].encode()).hexdigest()
        # Guard against regressions of the A1 leak: the 8 chars shown to the Router
        # must not reveal the case-id prefix (dep / test / conf).
        prefix = error["id"].split("_")[0]
        assert prefix not in sha[:8], f"commit_sha leaks the category for {error['id']}"
    return {
        "ci_logs":       error["ci_logs"],
        "ci_job_name":   "" if condition == "no_jobname" else error["ci_job_name"],
        "ci_conclusion": "failure",
        "commit_sha":    sha,
        "git_diff":      error.get("git_diff", ""),
    }


# ──────────────────────────────────────────────────────────────
# Metrics (no sklearn dependency)
# ──────────────────────────────────────────────────────────────

def compute_metrics(y_true: list, y_pred: list) -> dict:
    """Accuracy over all cases; macro-F1 over the 3 true classes (an 'unknown' prediction is a miss)."""
    n = len(y_true)
    acc = sum(t == p for t, p in zip(y_true, y_pred)) / n if n else 0.0
    f1s, per_class = [], {}
    for c in LABELS:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == c and p == c)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != c and p == c)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == c and p != c)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        per_class[c] = (prec, rec, f1)
        f1s.append(f1)
    return {"n": n, "accuracy": acc, "macro_f1": sum(f1s) / len(f1s), "per_class": per_class}


# ──────────────────────────────────────────────────────────────
# Router call
# ──────────────────────────────────────────────────────────────

def configure_provider(model: dict):
    """router.LLM_PROVIDER is read at import time, so patch the module global."""
    os.environ["LLM_PROVIDER"] = model["provider"]
    if model["provider"] == "ollama":
        os.environ["OLLAMA_MODEL"] = model.get("ollama_model", "llama3.1:8b")
    import agent.agents.router as router
    router.LLM_PROVIDER = model["provider"]
    return router


def call_router(router, state: dict, timeout: int):
    """Returns (category, confidence, parse_failed, error_str)."""
    pool = ThreadPoolExecutor(max_workers=1)
    fut = pool.submit(router.router_node, state)
    try:
        out = fut.result(timeout=timeout)
    except FutureTimeout:
        return "unknown", 0.0, False, f"timeout>{timeout}s"
    except Exception as e:                        # malformed JSON keys, API errors, ...
        return "unknown", 0.0, False, f"{type(e).__name__}: {e}"
    finally:
        pool.shutdown(wait=False)
    parse_failed = out.get("router_reasoning") == "Parsing failed"
    return out["error_category"], float(out.get("error_confidence") or 0.0), parse_failed, ""


def run_condition(model: dict, router, condition: str, cases: list, timeout: int, pause: float):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"router_dryrun_{condition}__{model['id']}.csv"
    rows, parse_fail, call_err, consecutive_err = [], 0, 0, 0
    print(f"\n=== {model['name']} ({model['id']}) | condition={condition} | {len(cases)} cases ===")
    for i, err in enumerate(cases, 1):
        cat, conf, pf, e = call_router(router, build_state(err, condition), timeout)
        parse_fail += int(pf)
        call_err += int(bool(e))
        consecutive_err = consecutive_err + 1 if e else 0
        if consecutive_err >= 5:      # bad key / provider down: do NOT save a fake 0% result
            raise SystemExit(f"Aborted: 5 consecutive Router call errors (last: {e}). Nothing saved.")
        if e:
            print(f"  [{i}/{len(cases)}] {err['id']}: ERROR {e}")
        rows.append({"case_id": err["id"], "true_category": err["category"],
                     "predicted_category": cat, "confidence": round(conf, 4)})
        if i % 10 == 0:
            ok = sum(r["true_category"] == r["predicted_category"] for r in rows)
            print(f"  [{i}/{len(cases)}] running accuracy {ok / i:.1%}")
        time.sleep(pause)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["case_id", "true_category", "predicted_category", "confidence"])
        w.writeheader()
        w.writerows(rows)
    m = compute_metrics([r["true_category"] for r in rows], [r["predicted_category"] for r in rows])
    unknown = sum(r["predicted_category"] == "unknown" for r in rows)
    print(f"  -> {path.name}\n  accuracy={m['accuracy']:.3f}  macro-F1={m['macro_f1']:.3f}  "
          f"unknown={unknown}  json_parse_fail={parse_fail}  call_errors={call_err}")
    for c, (p, r, f1) in m["per_class"].items():
        print(f"     {c:<11} P={p:.2f} R={r:.2f} F1={f1:.2f}")
    return {"model_id": model["id"], "model_name": model["name"], "condition": condition, "n": m["n"],
            "accuracy": round(m["accuracy"], 4), "macro_f1": round(m["macro_f1"], 4),
            "unknown_predictions": unknown, "json_parse_fail": parse_fail, "call_errors": call_err}


def append_summary(rows: list):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "router_dryrun_summary.csv"
    new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if new:
            w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description="Router-only dry-run (no fix, no CI, no memory)")
    ap.add_argument("--model-id", help="id from MODELS in benchmark.py (see --list-models)")
    ap.add_argument("--all", action="store_true", help="run every model in MODELS, sequentially")
    ap.add_argument("--list-models", action="store_true")
    ap.add_argument("--condition", choices=list(CONDITIONS) + list(CONTROL_CONDITIONS) + ["both"], default="both")
    ap.add_argument("--limit", type=int, default=0, help="first N cases only (smoke test)")
    ap.add_argument("--timeout", type=int, default=0, help="per-call timeout in s (default: model timeout)")
    ap.add_argument("--pause", type=float, default=0.0, help="seconds between calls (rate limits)")
    args = ap.parse_args()

    if args.list_models:
        for m in MODELS:
            print(f"{m['id']:<24} {m['provider']:<10} {m.get('ollama_model', ''):<18} {m['name']}")
        return
    if not args.all and not args.model_id:
        ap.error("pass --model-id <id>, --all or --list-models")

    models = MODELS if args.all else [m for m in MODELS if m["id"] == args.model_id]
    if not models:
        ap.error(f"unknown model id {args.model_id!r} (see --list-models)")
    cases = DATASET[: args.limit] if args.limit else DATASET
    conditions = CONDITIONS if args.condition == "both" else (args.condition,)

    for model in models:
        router = configure_provider(model)
        summary = [run_condition(model, router, c, cases, args.timeout or model["timeout"], args.pause)
                   for c in conditions]
        append_summary(summary)
        if model["provider"] == "ollama":         # release VRAM before the next model
            subprocess.run(["ollama", "stop", model.get("ollama_model", "")], capture_output=True)


if __name__ == "__main__":
    main()
