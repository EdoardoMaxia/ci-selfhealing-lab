"""
Controlled A/B of the Dependency Agent's first attempt (no CI, no GitHub, no memory).

Why: in the A3 rerun, Mistral 7B dropped from 42.00% to 25.33% SR while the Router was unchanged.
In the failing cases the first attempt rewrites requirements.txt WITHOUT pytest/pytest-cov and/or
with stray backticks, and later attempts return the file unchanged. This script isolates the cause:
same model, same cases, same state, two versions of dependency_agent.py:
    current  : the code on this branch (English prompts)
    italian  : the same file at --italian-ref (default origin/main, Italian prompts)
Swap --model-id to compare models/digests as well.

For each dependency case it rebuilds requirements.txt exactly as benchmark.inject_error does, calls
dependency_agent_node (attempt 1) in a temp dir and classifies the written file. "valid" is a FORMAT
proxy for CI success (keeps the base lines, no backticks, bad pin removed, no unchanged output); it is
NOT the CI outcome. Do NOT run it while a benchmark is running (shared Ollama/GPU and rate limits).

Usage (repo root):
  python experiments/ab_dependency_agent.py --model-id ollama_mistral7b --variants current italian
  python experiments/ab_dependency_agent.py --model-id ollama_mistral7b --variants current --limit 5   # smoke test
"""
import argparse
import csv
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

REQ_LINE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.\-\[\]]*\s*(==|>=|<=|~=|!=|<|>)\s*[0-9][A-Za-z0-9_.\-*+!]*$")


def build_injected(original: str, git_diff: str) -> str:
    """Same logic as benchmark.inject_error for category == dependency."""
    current = original
    added = [l[1:].strip() for l in git_diff.splitlines() if l.startswith("+")]
    for line in added:
        if line and line not in current:
            current += f"\n{line}"
    return current


def classify(original: str, injected: str, output: str, git_diff: str) -> list:
    """Return the list of problems of the file written by the agent ([] = format-valid)."""
    problems = []
    base = {l.strip() for l in original.splitlines() if l.strip()}
    bad = {l[1:].strip() for l in git_diff.splitlines() if l.startswith("+") and l[1:].strip()}
    lines = [l.strip() for l in output.splitlines() if l.strip()]
    if output.strip() == injected.strip():
        problems.append("unchanged")
    if "`" in output:
        problems.append("backtick")
    if not base <= set(lines):
        problems.append("dropped_base_lines")
    if bad & set(lines):
        problems.append("bad_pin_kept")
    if any(not REQ_LINE.match(l.replace("`", "")) and not l.startswith("#") for l in lines):
        problems.append("invalid_line")
    return problems


def load_variant(name: str, ref: str, tmpdir: Path):
    if name == "current":
        from agent.agents import dependency_agent as mod
        return mod
    src = subprocess.run(["git", "show", f"{ref}:agent/agents/dependency_agent.py"],
                         capture_output=True, text=True, check=True).stdout
    path = tmpdir / "dependency_agent_it.py"
    path.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("dependency_agent_it", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser(description="A/B of the Dependency Agent's first attempt (no CI)")
    ap.add_argument("--model-id", required=True, help="id from MODELS in benchmark.py")
    ap.add_argument("--variants", nargs="+", default=["current", "italian"], choices=["current", "italian"])
    ap.add_argument("--italian-ref", default="origin/main")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--out", default="experiments/results/ab_dependency")
    args = ap.parse_args()

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from experiments.dataset import DATASET
    from experiments.benchmark import MODELS, ORIGINAL_REQUIREMENTS
    from experiments.router_dryrun import configure_provider

    model = next((m for m in MODELS if m["id"] == args.model_id), None)
    if model is None:
        ap.error(f"unknown model id {args.model_id!r}")
    configure_provider(model)
    cases = [e for e in DATASET if e["category"] == "dependency"]
    cases = cases[: args.limit] if args.limit else cases
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {}
    with tempfile.TemporaryDirectory() as td:
        for variant in args.variants:
            mod = load_variant(variant, args.italian_ref, Path(td))
            rows, counts = [], Counter()
            print(f"\n=== {model['name']} | variant={variant} | {len(cases)} dependency cases x {args.repeats} ===")
            for err in cases:
                for rep in range(args.repeats):
                    repo = Path(td) / f"{err['id']}_{variant}_{rep}"
                    repo.mkdir()
                    injected = build_injected(ORIGINAL_REQUIREMENTS, err.get("git_diff", ""))
                    (repo / "requirements.txt").write_text(injected, encoding="utf-8")
                    state = {"ci_logs": err["ci_logs"], "git_diff": err.get("git_diff", ""), "repo_path": str(repo),
                             "attempt_number": 1, "attempts_history": [], "case_id": err["id"]}
                    try:
                        mod.dependency_agent_node(state)
                        output = (repo / "requirements.txt").read_text(encoding="utf-8")
                        problems = classify(ORIGINAL_REQUIREMENTS, injected, output, err.get("git_diff", ""))
                    except Exception as e:                     # API/timeout: record it, do not count as a format failure
                        output, problems = "", [f"error:{type(e).__name__}"]
                    valid = not problems
                    counts["valid" if valid else "invalid"] += 1
                    for p in problems:
                        counts[p] += 1
                    rows.append({"case_id": err["id"], "variant": variant, "rep": rep, "valid": int(valid),
                                 "problems": "|".join(problems), "output": output.replace("\n", "\\n")[:400]})
            path = out_dir / f"ab_dependency__{args.model_id}__{variant}.csv"
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
            n = len(rows)
            summary[variant] = counts
            print(f"  -> {path.name}\n  format-valid: {counts['valid']}/{n} ({100 * counts['valid'] / n:.1f}%)")
            for k, v in sorted(counts.items()):
                if k not in ("valid", "invalid"):
                    print(f"     {k:<20} {v}")
    print("\nSummary:", {v: dict(c) for v, c in summary.items()})


if __name__ == "__main__":
    main()
