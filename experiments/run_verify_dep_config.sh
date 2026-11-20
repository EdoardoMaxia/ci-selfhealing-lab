#!/usr/bin/env bash
# Failing-state verification for dependency + config (MSR revision, analysis A2 §9a). No LLM.
#
# For each of the 100 dependency/config cases: inject the error, commit the FULL failing state
# on a fix/ai-verify-* branch, wait for the CI of that commit, record whether it is NOT green.
# A control branch with the baseline state runs first and must be green (otherwise "no_run"
# would be meaningless). Runs are pushed in batches of 5, so they execute in parallel.
# Estimate: about 30-60 min for the 100 cases (depends on the GitHub Actions queue).
#
# Launch from the repo root (survives SSH disconnect):
#   nohup bash experiments/run_verify_dep_config.sh > verify_dep_config_master.log 2>&1 &
#   tail -f verify_dep_config_master.log
# Dry run (prints the commands, runs nothing): DRY_RUN=1 bash experiments/run_verify_dep_config.sh
# Resumable: a finished category leaves experiments/results/verify_dep_config/.done/<category>.
# Skip the local commit of the results: NO_COMMIT=1
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
[ -f .venv/bin/activate ] && source .venv/bin/activate

DRY="${DRY_RUN:-0}"
OUT=experiments/results/verify_dep_config
DONE=$OUT/.done
RESULTS_BRANCH=results-verify-dep-config
CI_SCOPE=(src app tests requirements.txt .github/workflows)
mkdir -p "$OUT" "$DONE"
ts() { date '+%Y-%m-%d %H:%M:%S'; }
say() { echo "[$(ts)] $*"; }
die() { say "ABORT: $*"; exit 1; }

say "=== verify dep/config start | branch $(git rev-parse --abbrev-ref HEAD) @ $(git rev-parse --short HEAD) ==="

# ── Prerequisites ──────────────────────────────────────────────────────────────
command -v python >/dev/null || die "python not found (activate the .venv)"
if [ "$DRY" != 1 ]; then
  [ "$(git rev-parse --abbrev-ref HEAD)" = "msr-revision" ] || die "not on branch msr-revision"
  [ -z "$(git status --porcelain --untracked-files=all -- "${CI_SCOPE[@]}")" ] \
    || die "uncommitted/untracked files under ${CI_SCOPE[*]}: they would end up in every failing state"
  pgrep -f "experiments/benchmark.py" >/dev/null && die "another experiments/benchmark.py is running (no parallel runs)"
  remote_heads=$(git ls-remote --heads origin) || die "git ls-remote origin failed (network / credentials)"
  pending=$(grep -c 'refs/heads/fix/ai-' <<<"$remote_heads")
  [ "$pending" = 0 ] || die "$pending fix/ai-* branch(es) on GitHub: another run may be active. If none is, remove them:
      python -c 'from experiments.benchmark import cleanup_fix_branches; cleanup_fix_branches()'"
  git fetch -q origin main || die "git fetch origin main failed"
  git diff --quiet HEAD origin/main -- "${CI_SCOPE[@]}" \
    || die "CI scope of HEAD differs from GitHub main: every failing state would carry these differences"
  # The token lives in .env (read by the benchmark): checked through check_api.py, not $GITHUB_TOKEN.
  python experiments/check_api.py --providers github || die "GitHub check failed (GITHUB_TOKEN / GITHUB_REPO in .env)"
  python -c "import yaml" 2>/dev/null || say "WARNING: PyYAML missing, the static workflow check of config cases is skipped"
  python -m pytest agent/tests/test_protocol_b.py agent/tests/test_verify_dep_config.py -q || die "unit tests failed"
  [ -z "$(git status --porcelain --untracked-files=all -- "${CI_SCOPE[@]}")" ] || die "unit tests left changes under the CI scope"
  say "prerequisites OK"
fi

# ── Verification, one category at a time ───────────────────────────────────────
FAILED=()
run_category() {   # run_category <category> <ci-timeout>
  local cat="$1" tmo="$2"
  if [ -f "$DONE/$cat" ]; then say "skip $cat (already done)"; return 0; fi
  say "START $cat (ci-timeout ${tmo}s)"
  [ "$DRY" = 1 ] && { echo "  python -u experiments/benchmark.py --verify-dep-config --category $cat --ci-timeout $tmo"; return 0; }
  python -u experiments/benchmark.py --verify-dep-config --category "$cat" --ci-timeout "$tmo" 2>&1 | tee "$OUT/log_$cat.txt"
  local rc=${PIPESTATUS[0]}
  if [ "$rc" = 0 ]; then touch "$DONE/$cat"; say "OK    $cat"
  else FAILED+=("$cat"); say "FAIL  $cat (exit $rc): control run not green, or inconclusive cases to re-run — see $OUT/log_$cat.txt"; fi
}
run_category dependency 600   # torch==2.0.0 (dep_010) downloads ~2 GB of wheels before failing or passing
run_category config 600

# ── Report ─────────────────────────────────────────────────────────────────────
if [ "$DRY" != 1 ] && [ -f "$OUT/verify_results.csv" ]; then
  python - "$OUT" <<'PY' | tee "$OUT/verify_summary.md"
import csv, sys, collections
rows = list(csv.DictReader(open(f"{sys.argv[1]}/verify_results.csv", encoding="utf-8")))
print("# Failing-state verification — dependency / config\n")
print("| Category | cases | verified failing | CI green (anomaly) | of which injection changed nothing | inconclusive |")
print("|---|---|---|---|---|---|")
for cat in ("dependency", "config"):
    rs = [r for r in rows if r["category"] == cat]
    if not rs: continue
    v = sum(r["verified_failing"] == "true" for r in rs)
    g = [r for r in rs if r["ci_conclusion"] == "success"]
    noop = sum(r["injection_applied"] == "false" for r in g)
    inc = sum(r["verified_failing"] != "true" and r["ci_conclusion"] != "success" for r in rs)
    print(f"| {cat} | {len(rs)} | {v} | {len(g)} | {noop} | {inc} |")
print("\nCI conclusions:", dict(collections.Counter(r["ci_conclusion"] for r in rows)))
print("\n## Cases that are NOT verified failing\n")
print("| Case | CI | run | notes |")
print("|---|---|---|---|")
for r in rows:
    if r["verified_failing"] != "true":
        print(f"| {r['case_id']} | {r['ci_conclusion']} | {r['ci_run_id']} | {r['notes'][:140]} |")
PY
fi

# ── Results branch (local commit through a temporary worktree, never pushed) ──
if [ "$DRY" != 1 ] && [ "${NO_COMMIT:-0}" != 1 ] && [ ${#FAILED[@]} -eq 0 ]; then
  wt=$(mktemp -d "${TMPDIR:-/tmp}/verify-dc-XXXXXX")
  if git show-ref --verify --quiet "refs/heads/$RESULTS_BRANCH"; then git worktree add -q "$wt" "$RESULTS_BRANCH"
  else git worktree add -q -b "$RESULTS_BRANCH" "$wt" HEAD; fi \
    && mkdir -p "$wt/$OUT" && cp -r "$OUT"/. "$wt/$OUT"/ && rm -rf "$wt/$OUT/.done" \
    && (cd "$wt" && git add -f "$OUT" && git commit -q -m "results: dependency/config failing-state verification ($(date +%Y-%m-%d))") \
    && say "results committed on $RESULTS_BRANCH (NOT pushed: git push origin $RESULTS_BRANCH)" \
    || say "WARNING: results NOT committed (they are in $OUT)"
  git worktree remove --force "$wt" 2>/dev/null
fi
say "=== DONE | failed: ${FAILED[*]:-none} ==="
[ ${#FAILED[@]} -eq 0 ]
