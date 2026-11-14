#!/usr/bin/env bash
# A3 memory-ablation rerun, unattended (MSR 2027 reviewer response, Q4).
#
# Order matters: --no-memory only disables SAVING, retrieval still hits a non-empty store.
# So: (1) 6 baselines on an EMPTY store, (2) Haiku calibration fills the store,
# (3) the other 5 models run read-only on it. Haiku's "memory" row = the calibration run.
#
# Launch from the repo root (survives SSH disconnect):
#   nohup bash experiments/run_a3_rerun.sh > a3_rerun_master.log 2>&1 &
#   tail -f a3_rerun_master.log
# Resumable: a finished step leaves experiments/results/a3_rerun/.done/<step>; re-launching skips it.
# Stop: kill the 'run_a3_rerun.sh' process (pkill -f run_a3_rerun.sh), then re-launch to resume.
# Dry run (prints the commands, runs nothing): DRY_RUN=1 bash experiments/run_a3_rerun.sh
# Optional extra read-only Haiku run on the populated store: READONLY_HAIKU=1
set -u
cd "$(dirname "$0")/.." || exit 1
[ -f .venv/bin/activate ] && source .venv/bin/activate

DRY="${DRY_RUN:-0}"
OUT=experiments/results/a3_rerun
LOGS=$OUT/logs
DONE=$OUT/.done
RES=experiments/results
BACKUP="$HOME/episodic_memory_sept2026_backup"
mkdir -p "$OUT" "$LOGS" "$DONE"
ts() { date '+%Y-%m-%d %H:%M:%S'; }
say() { echo "[$(ts)] $*"; }
die() { say "ABORT: $*"; exit 1; }

OLLAMA_TAGS=(qwen38-4k qwen3coder-4k llama31-4k mistral-4k)

store_stat() {   # prints: total success escalated with_case_id   (reads the live ChromaDB)
  PYTHONPATH=. python - <<'PY'
from agent.memory.episodic_store import get_collection
c = get_collection(); r = c.get(include=["metadatas"]); m = r["metadatas"] or []
print(len(m), sum(x.get("outcome") == "success" for x in m), sum(x.get("outcome") == "escalated" for x in m),
      sum(bool(x.get("case_id")) for x in m))
PY
}

collect() {      # move the CSV/JSON written since the step started into a3_rerun/
  local mark="$1"
  find "$RES" -maxdepth 1 -name 'benchmark_*.csv' -newer "$mark" -exec mv {} "$OUT"/ \;
  find "$RES" -maxdepth 1 -name 'benchmark_*.json' -newer "$mark" -exec mv {} "$OUT"/ \;
}

STEPS_OK=(); STEPS_FAIL=()
# step <name> <critical:0|1> <command...>
step() {
  local name="$1" crit="$2"; shift 2
  if [ -f "$DONE/$name" ]; then say "skip $name (already done)"; STEPS_OK+=("$name(prev)"); return 0; fi
  say "START $name :: $*"
  if [ "$DRY" = 1 ]; then return 0; fi
  local mark; mark=$(mktemp "$LOGS/.mark_XXXX")
  "$@" > "$LOGS/$name.log" 2>&1
  local rc=$?
  collect "$mark"; rm -f "$mark"
  if [ $rc -eq 0 ]; then
    touch "$DONE/$name"; STEPS_OK+=("$name"); say "OK    $name"
  else
    STEPS_FAIL+=("$name"); say "FAIL  $name (exit $rc) - see $LOGS/$name.log"
    [ "$crit" = 1 ] && die "critical step $name failed"
  fi
  return 0
}

stop_ollama() { [ "$DRY" = 1 ] || ollama stop "$1" >/dev/null 2>&1; }

say "=== A3 rerun start | branch $(git rev-parse --abbrev-ref HEAD) @ $(git rev-parse --short HEAD) ==="
if [ "$DRY" != 1 ]; then
  [ "$(git rev-parse --abbrev-ref HEAD)" = "msr-revision" ] || die "not on branch msr-revision"
  # Only the deterministic unit tests: test_config_agent/test_dependency_agent/test_end_to_end/
  # test_router/test_test_agent are integration SCRIPTS that call the LLM and GitHub at import time.
  python -m pytest agent/tests/test_memory_exclusion.py agent/tests/test_benchmark_state_leakage.py \
    agent/tests/test_router_dryrun_state.py -q || die "unit tests failed"
  python experiments/check_api.py --providers anthropic openai github || die "API/GitHub check failed (GITHUB_TOKEN in .env must be valid: the Fix Executor needs it)"
  read -r total _ <<<"$(store_stat)"
  if [ "${total:-0}" -gt 0 ] && [ ! -d "$BACKUP" ]; then cp -r data/episodic_memory "$BACKUP" && say "backup of the existing store ($total episodes) -> $BACKUP"; fi
fi

# ── 1. Baselines (store must be empty) ─────────────────────────────────────────
step base_haiku  1 python -u experiments/benchmark.py --provider anthropic --no-memory --clean-memory
if [ "$DRY" != 1 ]; then
  read -r total _ <<<"$(store_stat)"; [ "${total:-1}" = 0 ] || die "store not empty before baselines ($total episodes)"
fi
step base_gpt4o  0 python -u experiments/benchmark.py --provider openai --no-memory
for t in "${OLLAMA_TAGS[@]}"; do
  step "base_$t" 0 python -u experiments/benchmark.py --provider ollama --ollama-model "$t" --no-memory
  stop_ollama "$t"
  if [ "$DRY" != 1 ]; then read -r total _ <<<"$(store_stat)"; [ "${total:-1}" = 0 ] || die "store changed during baselines ($total episodes)"; fi
done

# ── 2. Calibration: Haiku with memory, clean store ─────────────────────────────
step calib_haiku 1 python -u experiments/benchmark.py --provider anthropic --clean-memory
if [ "$DRY" != 1 ]; then
  read -r total succ esc withcase <<<"$(store_stat)"
  say "store after calibration: total=$total success=$succ escalated=$esc with_case_id=$withcase"
  [ "$total" -gt 0 ] && [ "$withcase" = "$total" ] || die "episodes missing case_id (total=$total with_case_id=$withcase)"
  [ "$succ" -ge 100 ] || die "only $succ successful episodes (expected ~133) - check the Haiku run before continuing"
  echo "$total $succ $esc $withcase" > "$OUT/store_after_calibration.txt"
fi

# ── 3. Read-only runs on the populated store ───────────────────────────────────
ro_check() {
  [ "$DRY" = 1 ] && return 0
  read -r total _ <<<"$(store_stat)"
  [ "$total" = "$(cut -d' ' -f1 "$OUT/store_after_calibration.txt")" ] || die "store size changed during a read-only run ($total)"
}
step ro_gpt4o 0 python -u experiments/benchmark.py --provider openai --readonly-memory; ro_check
for t in "${OLLAMA_TAGS[@]}"; do
  step "ro_$t" 0 python -u experiments/benchmark.py --provider ollama --ollama-model "$t" --readonly-memory
  stop_ollama "$t"; ro_check
done
[ "${READONLY_HAIKU:-0}" = 1 ] && { step ro_haiku 0 python -u experiments/benchmark.py --provider anthropic --readonly-memory; ro_check; }

# ── 4. Analysis + summary ──────────────────────────────────────────────────────
if [ "$DRY" != 1 ]; then
  python experiments/a3_rerun_analysis.py --markdown > "$OUT/a3_rerun_analysis.md" 2>&1
  say "analysis -> $OUT/a3_rerun_analysis.md"
fi
say "=== DONE | ok: ${STEPS_OK[*]:-none} | failed: ${STEPS_FAIL[*]:-none} ==="
[ ${#STEPS_FAIL[@]} -eq 0 ]
