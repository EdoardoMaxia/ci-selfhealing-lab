#!/usr/bin/env bash
# F2 rerun on the corrected benchmark (MSR 2027 revision), unattended. Protocol: --failing-state
# (protocol B for every category: red pre-check on the full failing state, fixes branch from it).
# Set: the 78 cases not in experiments/excluded_cases.json (39 test, 35 dependency, 4 config).
#
#   0. preflight: branch msr-revision, CI scope clean and equal to GitHub main, no pending fix/ai-*
#      branches, no other benchmark running, unit tests, check_api.py, ollama list, disk space,
#      backup of the current store -> ~/episodic_memory_pre_f2_<date>
#   1. baseline, no memory, EMPTY store: 6 models x dependency + config (39 cases);
#      the "test" baseline is A2 (protocol B, 39 cases, 19 Nov), not rerun here
#   2. calibration: Haiku with memory ON, from an empty store, on the 78 cases; then backup
#      -> ~/episodic_memory_post_calib_f2_<date> and check that every episode carries case_id
#   3. memory arm: the other 5 models, --readonly-memory, on the 78 cases
#      (Haiku's memory row is the calibration run, as in A3)
#   4. summary (experiments/f2_rerun_summary.py) + local commit on results-f2-rerun (NOT pushed)
#
# Order matters: --no-memory only disables SAVING, retrieval still hits a non-empty store.
# A pre-check that is not red is never replaced: the case is skipped, logged here and counted
# in the summary under "skipped by reason" (expected 0).
#
# Launch from the repo root (survives SSH disconnect):
#   nohup bash experiments/run_f2_rerun.sh > f2_rerun_master.log 2>&1 &
#   tail -f f2_rerun_master.log
# Resumable: a finished step leaves experiments/results/f2_rerun/.done/<step>; re-launching skips it.
# Stop: pkill -f run_f2_rerun.sh (then also the running experiments/benchmark.py), re-launch to resume.
# Dry run (prints the commands, runs nothing): DRY_RUN=1 bash experiments/run_f2_rerun.sh
# Do not edit, pull or check out while it runs: the script is parsed in full before it starts,
# and every step aborts if the code fingerprint (HEAD + tracked experiments/ and agent/ code) changed.
# Tunables: MIN_FREE_GB (default 10), MIN_CALIB_SUCCESS (default 50 successful Haiku episodes),
#           A2_DIR (default experiments/results/a2_test_rerun), MASTER_LOG (default f2_rerun_master.log)
set -u

main() {
cd "$(dirname "$0")/.." || exit 1
[ -f .venv/bin/activate ] && source .venv/bin/activate

DRY="${DRY_RUN:-0}"
OUT=experiments/results/f2_rerun
LOGS=$OUT/logs
DONE=$OUT/.done
RESULTS_BRANCH=results-f2-rerun
A2_DIR="${A2_DIR:-experiments/results/a2_test_rerun}"
MASTER_LOG="${MASTER_LOG:-f2_rerun_master.log}"
CI_SCOPE=(src app tests requirements.txt .github/workflows)
OLLAMA_TAGS=(qwen38-4k qwen3coder-4k llama31-4k mistral-4k)
mkdir -p "$OUT" "$LOGS" "$DONE"
[ -f "$OUT/.date" ] || date +%Y%m%d > "$OUT/.date"          # fixed at the first launch (resume-safe)
RUN_DATE=$(cat "$OUT/.date")
BACKUP_PRE="$HOME/episodic_memory_pre_f2_$RUN_DATE"
BACKUP_CALIB="$HOME/episodic_memory_post_calib_f2_$RUN_DATE"

ts()  { date '+%Y-%m-%d %H:%M:%S'; }
say() { echo "[$(ts)] $*"; }
die() { say "ABORT: $*"; exit 1; }

code_fingerprint() {   # HEAD + content of the tracked code the runs depend on
  { git rev-parse HEAD
    git ls-files -z -- 'experiments/*.py' 'experiments/*.json' 'experiments/*.sh' 'agent/*.py' \
        ':!experiments/results' | xargs -0 sha256sum
  } | sha256sum | cut -c1-16
}

store_stat() {   # prints: total success escalated with_case_id   (reads the live ChromaDB)
  PYTHONPATH=. python - <<'PY' 2>/dev/null | tail -n 1
from agent.memory.episodic_store import get_collection
c = get_collection(); r = c.get(include=["metadatas"]); m = r["metadatas"] or []
print(len(m), sum(x.get("outcome") == "success" for x in m), sum(x.get("outcome") == "escalated" for x in m),
      sum(bool(x.get("case_id")) for x in m))
PY
}

STEPS_OK=(); STEPS_FAIL=(); LAST_RAN=0
# step <name> <critical:0|1> <command...>     (LAST_RAN=1 only if the step actually ran now)
step() {
  local name="$1" crit="$2"; shift 2
  LAST_RAN=0
  if [ -f "$DONE/$name" ]; then say "skip $name (already done)"; STEPS_OK+=("$name(prev)"); return 0; fi
  say "START $name :: $*"
  [ "$DRY" = 1 ] && return 0
  LAST_RAN=1
  [ "$(code_fingerprint)" = "$FINGERPRINT" ] || die "code changed since the launch (HEAD or experiments/, agent/): no mixed runs"
  local t0; t0=$(date +%s)
  "$@" > "$LOGS/$name.log" 2>&1
  local rc=$?
  printf '%s\t%s\t%s\t%s\n' "$name" "$t0" "$(date +%s)" "$rc" >> "$OUT/steps.tsv"
  # pre-checks that were not red, non-injectable cases: logged, never replaced
  grep -hE "ANOMALY|injection not applied|pre-check failed" "$LOGS/$name.log" | sed 's/^/      /'
  if [ $rc -eq 0 ]; then
    touch "$DONE/$name"; STEPS_OK+=("$name"); say "OK    $name ($(( ($(date +%s) - t0) / 60 )) min)"
  else
    STEPS_FAIL+=("$name"); say "FAIL  $name (exit $rc) - see $LOGS/$name.log"
    [ "$crit" = 1 ] && die "critical step $name failed"
  fi
  return 0
}

stop_ollama() { [ "$DRY" = 1 ] || ollama stop "$1" >/dev/null 2>&1; }
store_must_be() {   # store_must_be <total> <context>   (only after a step that ran in this launch)
  [ "$DRY" = 1 ] || [ "$LAST_RAN" = 0 ] && return 0
  local total; read -r total _ <<<"$(store_stat)"
  [ "${total:-x}" = "$1" ] || die "$2: store has ${total:-?} episodes, expected $1"
}

say "=== F2 rerun start | branch $(git rev-parse --abbrev-ref HEAD) @ $(git rev-parse --short HEAD) | date tag $RUN_DATE ==="

# ── 0. Preflight ───────────────────────────────────────────────────────────────
if [ "$DRY" != 1 ]; then
  [ "$(git rev-parse --abbrev-ref HEAD)" = "msr-revision" ] || die "not on branch msr-revision"
  pgrep -f "experiments/benchmark.py" >/dev/null && die "another experiments/benchmark.py is running (no parallel runs)"
  [ -z "$(git status --porcelain --untracked-files=all -- "${CI_SCOPE[@]}")" ] \
    || die "uncommitted/untracked files under ${CI_SCOPE[*]}: they would end up in every failing state"
  remote_heads=$(git ls-remote --heads origin) || die "git ls-remote origin failed (network / credentials)"
  pending=$(grep -c 'refs/heads/fix/ai-' <<<"$remote_heads")
  [ "$pending" = 0 ] || die "$pending fix/ai-* branch(es) on GitHub: another run may be active. If none is, remove them:
      python -c 'from experiments.benchmark import cleanup_fix_branches; cleanup_fix_branches()'"
  git fetch -q origin main || die "git fetch origin main failed"
  git diff --quiet HEAD origin/main -- "${CI_SCOPE[@]}" \
    || die "CI scope of HEAD differs from GitHub main: every failing state would carry these differences"
  python -m pytest agent/tests/test_f1_failing_state.py agent/tests/test_protocol_b.py \
    agent/tests/test_verify_dep_config.py agent/tests/test_memory_exclusion.py \
    agent/tests/test_benchmark_state_leakage.py agent/tests/test_fix_executor_modified_file.py \
    agent/tests/test_f2_rerun.py -q || die "unit tests failed"
  [ -z "$(git status --porcelain --untracked-files=all -- "${CI_SCOPE[@]}")" ] || die "unit tests left changes under the CI scope"
  python experiments/check_api.py --providers anthropic openai github || die "API/GitHub check failed (.env)"
  for t in "${OLLAMA_TAGS[@]}"; do
    ollama list | awk 'NR>1 {print $1}' | grep -q "^$t\(:\|$\)" || die "Ollama model $t not found (ollama list)"
  done
  for d in . "$HOME"; do
    free_gb=$(df -Pk "$d" | awk 'NR==2 {print int($4/1048576)}')
    [ "$free_gb" -ge "${MIN_FREE_GB:-10}" ] || die "only ${free_gb} GB free on $(df -P "$d" | awk 'NR==2 {print $6}') (MIN_FREE_GB=${MIN_FREE_GB:-10})"
  done
  [ -d "$A2_DIR" ] || say "WARNING: $A2_DIR not found: the summary will lack the A2 test baseline (set A2_DIR)"
  if [ ! -d "$BACKUP_PRE" ]; then
    cp -r data/episodic_memory "$BACKUP_PRE" || die "backup of the store failed"
    read -r total succ _ <<<"$(store_stat)"
    say "backup of the current store ($total episodes) -> $BACKUP_PRE"
    echo "$total $succ" > "$OUT/store_before_f2.txt"
  else
    say "store backup already present: $BACKUP_PRE"
  fi
  FINGERPRINT=$(code_fingerprint); echo "$FINGERPRINT $(git rev-parse HEAD)" > "$OUT/code_fingerprint.txt"
  say "preflight OK | code fingerprint $FINGERPRINT"
fi

BASE=(--failing-state --no-memory --output-dir "$OUT")
FULL=(--failing-state --output-dir "$OUT")

# ── 1. Baseline, no memory, empty store: dependency + config ───────────────────
step base_haiku_dependency 1 python -u experiments/benchmark.py --provider anthropic --category dependency "${BASE[@]}" --clean-memory
store_must_be 0 "before the baselines"
step base_haiku_config 0 python -u experiments/benchmark.py --provider anthropic --category config "${BASE[@]}"
store_must_be 0 "during the baselines"
for c in dependency config; do
  step "base_gpt4o_$c" 0 python -u experiments/benchmark.py --provider openai --category "$c" "${BASE[@]}"
  store_must_be 0 "during the baselines"
done
for t in "${OLLAMA_TAGS[@]}"; do
  for c in dependency config; do
    step "base_${t}_$c" 0 python -u experiments/benchmark.py --provider ollama --ollama-model "$t" --category "$c" "${BASE[@]}"
    store_must_be 0 "during the baselines"
  done
  stop_ollama "$t"
done

# ── 2. Calibration: Haiku with memory ON, from an empty store, 78 cases ────────
step calib_haiku 1 python -u experiments/benchmark.py --provider anthropic "${FULL[@]}" --clean-memory
if [ "$DRY" != 1 ] && [ ! -f "$OUT/store_after_calibration.txt" ]; then
  read -r total succ esc withcase <<<"$(store_stat)"
  say "store after calibration: total=$total success=$succ escalated=$esc with_case_id=$withcase"
  [ "${total:-0}" -gt 0 ] && [ "$withcase" = "$total" ] || die "episodes missing case_id (total=$total with_case_id=$withcase)"
  [ "$succ" -ge "${MIN_CALIB_SUCCESS:-50}" ] || die "only $succ successful episodes (MIN_CALIB_SUCCESS=${MIN_CALIB_SUCCESS:-50}): check the Haiku run before continuing"
  [ -d "$BACKUP_CALIB" ] || cp -r data/episodic_memory "$BACKUP_CALIB" || die "backup after calibration failed"
  tar czf "$OUT/store_after_calibration.tgz" -C data episodic_memory
  echo "$total $succ $esc $withcase" > "$OUT/store_after_calibration.txt"
  say "store after calibration -> $BACKUP_CALIB and $OUT/store_after_calibration.tgz"
fi
CALIB_TOTAL=$([ -f "$OUT/store_after_calibration.txt" ] && cut -d' ' -f1 "$OUT/store_after_calibration.txt" || echo 0)

# ── 3. Memory arm: the other 5 models, read-only, 78 cases ─────────────────────
step ro_gpt4o 0 python -u experiments/benchmark.py --provider openai "${FULL[@]}" --readonly-memory
store_must_be "$CALIB_TOTAL" "after a read-only run"
for t in "${OLLAMA_TAGS[@]}"; do
  step "ro_$t" 0 python -u experiments/benchmark.py --provider ollama --ollama-model "$t" "${FULL[@]}" --readonly-memory
  stop_ollama "$t"
  store_must_be "$CALIB_TOTAL" "after a read-only run"
done

# ── 4. Summary + local commit (never pushed) ───────────────────────────────────
if [ "$DRY" != 1 ]; then
  python experiments/f2_rerun_summary.py --dir "$OUT" --a2-dir "$A2_DIR" --steps "$OUT/steps.tsv" \
    > "$OUT/f2_rerun_summary.md" 2> "$LOGS/summary.err" || say "WARNING: summary failed, see $LOGS/summary.err"
  cat "$OUT/f2_rerun_summary.md"
fi
say "=== DONE | ok: ${STEPS_OK[*]:-none} | failed: ${STEPS_FAIL[*]:-none} ==="

if [ "$DRY" != 1 ] && [ ${#STEPS_FAIL[@]} -eq 0 ]; then
  [ -f "$MASTER_LOG" ] && cp "$MASTER_LOG" "$OUT/"
  wt=$(mktemp -d "${TMPDIR:-/tmp}/f2-rerun-XXXXXX")
  if git show-ref --verify --quiet "refs/heads/$RESULTS_BRANCH"; then git worktree add -q "$wt" "$RESULTS_BRANCH"
  else git worktree add -q -b "$RESULTS_BRANCH" "$wt" HEAD; fi \
    && mkdir -p "$wt/$OUT" && cp -r "$OUT"/. "$wt/$OUT"/ && rm -rf "$wt/$OUT/.done" \
    && (cd "$wt" && git add -f "$OUT" && git commit -q -m "results: F2 rerun on the corrected benchmark (78 cases, --failing-state) ($(date +%Y-%m-%d))") \
    && say "results committed on $RESULTS_BRANCH (NOT pushed: git push origin $RESULTS_BRANCH)" \
    || say "WARNING: results NOT committed (they are in $OUT)"
  git worktree remove --force "$wt" 2>/dev/null
elif [ "$DRY" != 1 ]; then
  say "results NOT committed: failed steps ${STEPS_FAIL[*]} (re-launch to retry them; finished steps are skipped)"
fi
[ ${#STEPS_FAIL[@]} -eq 0 ]
}

main "$@"
exit $?
