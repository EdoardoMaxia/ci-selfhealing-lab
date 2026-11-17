#!/usr/bin/env bash
# A2 rerun of the "test" category with protocol B, unattended
# (MSR 2027 reviewer response, concern 2 / Q3; professor's option B).
#
# Protocol B: the agent may modify ONLY test files. The 11 cases whose error is injected
# outside the test file are excluded (39 valid test cases, 139 overall). For every valid
# case the CI must be RED on the full failed state before the agent runs, and every fix
# branch starts from that state (see experiments/benchmark.py, section PROTOCOL B).
#
# Steps:
#   0. preflight: branch msr-revision, clean CI scope, CI scope == GitHub main, no other
#      benchmark running, no pending fix/ai-* branches on GitHub, memory store backed up
#      and emptied, deterministic unit tests, API / GitHub / Ollama checks
#   1. --verify-excluded (no LLM, ~15 min): the 11 excluded cases, CI with only the test
#      file (expected green) vs full failed state (expected red). Runs FIRST: it exercises
#      the whole new CI plumbing before the 234 model runs.
#   2. 6 models x 50 test cases (11 logged as excluded, 39 run) with
#      --test-protocol-b --no-memory on an EMPTY store: --no-memory only disables saving,
#      retrieval at attempt 3 would still read a populated store.
#   3. summary markdown, then the results are committed LOCALLY on branch
#      results-a2-test-rerun through a temporary worktree (never pushed).
#
# Launch from the repo root (survives SSH disconnect):
#   nohup bash experiments/run_a2_test_rerun.sh > a2_test_rerun_master.log 2>&1 &
#   tail -f a2_test_rerun_master.log
# Resumable: a finished step leaves experiments/results/a2_test_rerun/.done/<step>; re-launching skips it.
# Stop: pkill -f run_a2_test_rerun.sh; pkill -f experiments/benchmark.py — then re-launch to resume
#       (the interrupted step restarts from scratch; delete its partial CSV if you want).
# Dry run (prints the commands, runs nothing): DRY_RUN=1 bash experiments/run_a2_test_rerun.sh
# Skip the results commit: NO_COMMIT=1
set -u
cd "$(dirname "$0")/.." || exit 1
[ -f .venv/bin/activate ] && source .venv/bin/activate

DRY="${DRY_RUN:-0}"
OUT=experiments/results/a2_test_rerun
LOGS=$OUT/logs
DONE=$OUT/.done
RESULTS_BRANCH=results-a2-test-rerun
CI_SCOPE=(src app tests requirements.txt .github/workflows)
OLLAMA_TAGS=(qwen38-4k qwen3coder-4k llama31-4k mistral-4k)
COMMON=(--category test --test-protocol-b --no-memory --output-dir "$OUT")
mkdir -p "$OUT" "$LOGS" "$DONE"
ts() { date '+%Y-%m-%d %H:%M:%S'; }
say() { echo "[$(ts)] $*"; }
die() { say "ABORT: $*"; exit 1; }

store_stat() {   # prints: total success escalated with_case_id   (reads the live ChromaDB)
  PYTHONPATH=. python - <<'PY' 2>/dev/null | tail -n 1
from agent.memory.episodic_store import get_collection
c = get_collection(); r = c.get(include=["metadatas"]); m = r["metadatas"] or []
print(len(m), sum(x.get("outcome") == "success" for x in m), sum(x.get("outcome") == "escalated" for x in m),
      sum(bool(x.get("case_id")) for x in m))
PY
}
store_empty() {
  [ "$DRY" = 1 ] && return 0
  local total; read -r total _ <<<"$(store_stat)"
  [ "${total:-1}" = 0 ] || die "memory store not empty ($total episodes): the no-memory baseline needs an empty store"
}

# precheck_guard <model_id>: stop if the pre-check was not red on several valid cases of that model
precheck_guard() {
  [ "$DRY" = 1 ] && return 0
  local bad
  bad=$(python - "$OUT" "$1" <<'PY'
import csv, sys, glob
files = sorted(glob.glob(f"{sys.argv[1]}/benchmark_*_{sys.argv[2]}_*_protob.csv"))
rows = list(csv.DictReader(open(files[-1], encoding="utf-8"))) if files else []
print(sum(r["final_status"] in ("precheck_green", "precheck_error", "injection_failed") for r in rows))
PY
)
  if [ "${bad:-0}" -gt 0 ]; then say "WARNING: $bad case(s) of $1 skipped by the pre-check (see the CSV / benchmark.log)"; fi
  [ "${bad:-0}" -lt 5 ] || die "$bad cases of $1 not red on the failed state: check the pre-check before spending more runs"
}

STEPS_OK=(); STEPS_FAIL=()
# step <name> <critical:0|1> <command...>
step() {
  local name="$1" crit="$2"; shift 2
  if [ -f "$DONE/$name" ]; then say "skip $name (already done)"; STEPS_OK+=("$name(prev)"); return 0; fi
  say "START $name :: $*"
  if [ "$DRY" = 1 ]; then return 0; fi
  "$@" > "$LOGS/$name.log" 2>&1
  local rc=$?
  if [ $rc -eq 0 ]; then
    touch "$DONE/$name"; STEPS_OK+=("$name"); say "OK    $name"
  else
    STEPS_FAIL+=("$name"); say "FAIL  $name (exit $rc) - see $LOGS/$name.log"
    [ "$crit" = 1 ] && die "critical step $name failed"
  fi
  return 0
}

stop_ollama() { [ "$DRY" = 1 ] || ollama stop "$1" >/dev/null 2>&1; }

commit_results() {
  [ "$DRY" = 1 ] || [ "${NO_COMMIT:-0}" = 1 ] && return 0
  local wt; wt=$(mktemp -d "${TMPDIR:-/tmp}/a2-results-XXXXXX")
  if git show-ref --verify --quiet "refs/heads/$RESULTS_BRANCH"; then
    git worktree add -q "$wt" "$RESULTS_BRANCH"
  else
    git worktree add -q -b "$RESULTS_BRANCH" "$wt" HEAD
  fi || { say "WARNING: git worktree failed, results NOT committed (they are in $OUT)"; return 0; }
  mkdir -p "$wt/$OUT" && cp -r "$OUT"/. "$wt/$OUT"/ && rm -rf "$wt/$OUT/.done"
  if (cd "$wt" && git add -f "$OUT" && git commit -q -m "results(a2): test category rerun with protocol B ($(date +%Y-%m-%d))"); then
    say "results committed on $RESULTS_BRANCH @ $(git rev-parse --short "$RESULTS_BRANCH") (NOT pushed: git push origin $RESULTS_BRANCH)"
  else
    say "WARNING: nothing committed on $RESULTS_BRANCH"
  fi
  git worktree remove --force "$wt"
}

# ── 0. Preflight ───────────────────────────────────────────────────────────────
say "=== A2 test rerun (protocol B) start | branch $(git rev-parse --abbrev-ref HEAD) @ $(git rev-parse --short HEAD) ==="
if [ "$DRY" != 1 ]; then
  [ "$(git rev-parse --abbrev-ref HEAD)" = "msr-revision" ] || die "not on branch msr-revision"
  [ -z "$(git status --porcelain --untracked-files=all -- "${CI_SCOPE[@]}")" ] \
    || die "uncommitted/untracked files under ${CI_SCOPE[*]}: the pre-check would push them as part of every failed state"
  pgrep -f "experiments/benchmark.py" >/dev/null && die "another experiments/benchmark.py is running (no parallel runs: fix/ai-* cleanup)"
  pgrep -f "run_a3_rerun.sh" >/dev/null && die "run_a3_rerun.sh is running"

  remote_heads=$(git ls-remote --heads origin) || die "git ls-remote origin failed (network / credentials)"
  pending=$(grep -c 'refs/heads/fix/ai-' <<<"$remote_heads")
  [ "$pending" = 0 ] || die "$pending fix/ai-* branch(es) on GitHub: another benchmark may be running. If none is, remove them:
      python -c 'from experiments.benchmark import cleanup_fix_branches; cleanup_fix_branches()'"

  git fetch -q origin main || die "git fetch origin main failed"
  git diff --quiet HEAD origin/main -- "${CI_SCOPE[@]}" \
    || die "CI scope of HEAD differs from GitHub main: every pre-check would carry these differences ($(git diff --name-only HEAD origin/main -- "${CI_SCOPE[@]}" | tr '\n' ' '))"

  read -r total _ <<<"$(store_stat)"
  if [ "${total:-0}" -gt 0 ]; then
    BACKUP="$HOME/episodic_memory_pre_a2_$(date +%Y%m%d_%H%M%S)"
    cp -r data/episodic_memory "$BACKUP" || die "backup of the memory store failed"
    say "backup of the existing store ($total episodes) -> $BACKUP"
  fi

  # Only the deterministic unit tests (test_config_agent, test_dependency_agent, test_end_to_end,
  # test_router, test_test_agent, test_memory are integration scripts that call the LLM at import).
  python -m pytest agent/tests/test_protocol_b.py agent/tests/test_fix_executor_modified_file.py \
    agent/tests/test_benchmark_inject_error.py agent/tests/test_memory_exclusion.py \
    agent/tests/test_benchmark_state_leakage.py agent/tests/test_router_dryrun_state.py -q \
    || die "unit tests failed"
  [ -z "$(git status --porcelain --untracked-files=all -- "${CI_SCOPE[@]}")" ] || die "unit tests left changes under the CI scope"

  python experiments/check_api.py --providers anthropic openai github || die "API/GitHub check failed"
  command -v ollama >/dev/null || die "ollama not found"
  for t in "${OLLAMA_TAGS[@]}"; do
    ollama list | awk 'NR>1 {print $1}' | grep -q "^$t\(:\|$\)" || die "Ollama model $t not found (ollama list)"
  done

  PYTHONPATH=. python -c "from experiments.benchmark import clean_chromadb; clean_chromadb()" >/dev/null 2>&1
  store_empty
  say "preflight OK — memory store empty"
fi

# ── 1. The 11 excluded cases under the old protocol (documentation) ────────────
step verify_excluded 1 python -u experiments/benchmark.py --verify-excluded --output-dir "$OUT"

# ── 2. 6 models x test category, protocol B, no memory, empty store ────────────
step haiku 1 python -u experiments/benchmark.py --provider anthropic "${COMMON[@]}"
store_empty; precheck_guard anthropic_haiku
step gpt4o 0 python -u experiments/benchmark.py --provider openai "${COMMON[@]}"
store_empty; precheck_guard openai_gpt4o
for t in "${OLLAMA_TAGS[@]}"; do
  step "$t" 0 python -u experiments/benchmark.py --provider ollama --ollama-model "$t" "${COMMON[@]}"
  stop_ollama "$t"
  store_empty
done

# ── 3. Summary + results branch ────────────────────────────────────────────────
if [ "$DRY" != 1 ]; then
  python experiments/a2_test_rerun_summary.py --dir "$OUT" > "$OUT/a2_test_rerun_summary.md" 2>&1
  say "summary -> $OUT/a2_test_rerun_summary.md"
fi
commit_results
say "=== DONE | ok: ${STEPS_OK[*]:-none} | failed: ${STEPS_FAIL[*]:-none} ==="
[ ${#STEPS_FAIL[@]} -eq 0 ]
