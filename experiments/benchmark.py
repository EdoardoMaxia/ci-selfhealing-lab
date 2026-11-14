"""
Experimental evaluation script
Self-Healing CI/CD Pipeline — Multi-Model Benchmark

Runs the system on all dataset errors for every configured model,
measuring Success Rate, latency, attempt distribution and JSON parse failures.
Saves the results as CSV files ready for the paper figures.

Usage:
    # Dry-run on Anthropic (Router only, no real CI, no memory)
    python experiments/benchmark.py --provider anthropic --dry-run

    # Full run on Anthropic (with real CI, no memory)
    python experiments/benchmark.py --provider anthropic --no-memory

    # Ablation study with memory enabled
    python experiments/benchmark.py --provider anthropic

    # A single category only
    python experiments/benchmark.py --provider groq --category dependency --no-memory

    # Specific Ollama model
    python experiments/benchmark.py --provider ollama --ollama-model llama31-4k --no-memory

    # Quick test (5 errors per model)
    python experiments/benchmark.py --provider anthropic --dry-run --limit 5
"""

import os
import sys
import hashlib
import csv
import time
import json
import fnmatch
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.dataset import DATASET

# ══════════════════════════════════════════════════════════════
# MODEL CONFIGURATION
# ══════════════════════════════════════════════════════════════

MODELS = [
    {
        "id":       "anthropic_haiku",
        "provider": "anthropic",
        "name":     "Claude Haiku",
        "type":     "proprietary",
        "timeout":  300,
    },
    {
        "id":       "groq_llama70b",
        "provider": "groq",
        "name":     "Llama 3.3 70B (Groq)",
        "type":     "open-source-cloud",
        "timeout":  300,
    },
    {
        "id":       "ollama_llama8b",
        "provider": "ollama",
        "ollama_model": "llama31-4k",
        "name":     "Llama 3.1 8B",
        "type":     "open-source-local",
        "timeout":  900, # <-- previously set to 600 but better to raise it
    },
    {
        "id":       "ollama_mistral7b",
        "provider": "ollama",
        "ollama_model": "mistral-4k",
        "name":     "Mistral 7B",
        "type":     "open-source-local",
        "timeout":  900, # <-- previously set to 600 but better to raise it
    },
    {
        "id":       "ollama_llama70b",
        "provider": "ollama",
        "ollama_model": "llama3.3:70b",
        "name":     "Llama 3.3 70B",
        "type":     "open-source-local",
        "timeout":  900,
    },
    {
        "id":       "ollama_qwen38_27b",
        "provider": "ollama",
        "ollama_model": "qwen38-4k",
        "name":     "Qwen3.8 27B",
        "type":     "open-source-local",
        "timeout":  900,
    },
    {
        "id":       "ollama_qwen3coder_30b",
        "provider": "ollama",
        "ollama_model": "qwen3coder-4k",
        "name":     "Qwen3-Coder 30B",
        "type":     "open-source-local",
        "timeout":  900,
    },

    {
        "id":       "openai_gpt4o",
        "provider": "openai",
        "name":     "GPT-4o",
        "type":     "proprietary",
        "timeout":  300,
    },
]

# ══════════════════════════════════════════════════════════════
# PATH OUTPUT
# ══════════════════════════════════════════════════════════════

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════
# LOGGING
# ══════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(RESULTS_DIR / "benchmark.log", encoding="utf-8")
    ]
)
log = logging.getLogger("benchmark")

# ══════════════════════════════════════════════════════════════
# CHROMADB MANAGEMENT — cleanup and skip
# ══════════════════════════════════════════════════════════════

def clean_chromadb():
    """
    Deletes all the episodes from ChromaDB.
    To be called before a benchmark with memory enabled
    in order to start from a clean state.
    """
    try:
        from agent.memory.episodic_store import get_collection
        col   = get_collection()
        count = col.count()
        if count > 0:
            # ChromaDB requires a where filter for delete — use $or over all outcomes
            col.delete(where={
                "$or": [
                    {"outcome": {"$eq": "success"}},
                    {"outcome": {"$eq": "escalated"}},
                    {"outcome": {"$eq": "failed"}},
                ]
            })
            log.info(f"ChromaDB: removed {count} episodes")
        else:
            log.info("ChromaDB: already empty")
    except Exception as e:
        log.warning(f"ChromaDB cleanup failed: {e}")


# ══════════════════════════════════════════════════════════════
# FILE RESET — deterministic state for every test
# ══════════════════════════════════════════════════════════════

ORIGINAL_REQUIREMENTS = "pytest==7.4.0\npytest-cov==4.1.0\n"


# Test files created for Group 1 (see experiments/CHANGELOG_DATASET.md).
# Without this whitelist reset_files() would delete them on every run, since
# it removes any tests/*.py not listed here.
GROUP1_TEST_FILES = {
    "test_utils.py", "test_api.py", "test_models.py", "test_math.py",
    "test_list.py", "test_service.py", "test_auth.py", "test_db.py",
    "test_mock.py", "test_config.py", "test_validator.py",
    "test_integration.py", "test_serializer.py", "test_parser.py",
    "test_payment.py", "test_orders.py", "test_loader.py", "test_import.py",
    "test_notify.py", "test_registry.py", "test_legacy.py", "test_dates.py",
    "test_settings.py", "test_sampler.py", "test_validation.py",
    "test_scheduler.py", "test_reports.py", "test_logger.py",
    "test_billing_cycle.py",
}

# Test files created to replace the 15 previously excluded "test" cases
# (see experiments/CHANGELOG_DATASET.md) — same logic as GROUP1_TEST_FILES.
REPLACEMENT_TEST_FILES = {
    "test_worker.py", "test_weather.py", "test_export.py", "test_report.py",
    "test_queue.py", "test_cache.py", "test_concurrent.py", "test_metrics.py",
    "test_image_processing.py", "test_dedup.py", "test_stats.py",
    "test_recommender.py", "test_upload.py",
}

ALLOWED_TEST_FILES = (
    {"test_calculator.py", "test_async.py"}
    | GROUP1_TEST_FILES
    | REPLACEMENT_TEST_FILES
)

# Paths (relative to the repo root) of all the source/app/test/fixture files
# created for Group 1 that must be restored from git on every reset_files()
# (they can be modified both by the injection and by an agent fix).
GROUP1_RESTORE_PATHS = [
    # src/
    "src/calculator.py", "src/utils.py", "src/models.py", "src/services.py",
    "src/auth.py", "src/db.py", "src/mailer.py", "src/config.py",
    "src/validator.py", "src/integration_db.py", "src/serializer.py",
    "src/parser.py", "src/api.py", "src/orders.py", "src/loader.py",
    "src/importer.py", "src/registry.py", "src/legacy.py", "src/settings.py",
    "src/sampler.py", "src/validation.py", "src/scheduler.py",
    "src/reports.py", "src/logger.py", "src/billing_cycle.py",
    # src/ — created to replace the 15 previously excluded "test" cases
    "src/fetcher.py", "src/cache.py", "src/counter.py", "src/worker.py",
    "src/weather.py", "src/exporter.py", "src/summary.py", "src/pipeline.py",
    "src/metrics.py", "src/image_cache.py", "src/dedup.py", "src/stats.py",
    "src/recommender.py", "src/upload.py",
    # app/
    "app/__init__.py", "app/billing/__init__.py", "app/billing/payment.py",
    "app/notify.py",
    # tests/ (content, not only existence — see GROUP1_TEST_FILES /
    # REPLACEMENT_TEST_FILES for the whitelist)
    "tests/test_async.py",
    *[f"tests/{name}" for name in GROUP1_TEST_FILES],
    *[f"tests/{name}" for name in REPLACEMENT_TEST_FILES],
    # data fixtures
    "tests/data/sample.csv", "tests/fixtures/sample.json",
]


def reset_files():
    """
    Restores all modifiable files to their correct state
    before introducing the specific error of the test case.
    Called automatically before every single error.
    """
    repo_root = Path(".")

    # 1. requirements.txt — clean version
    (repo_root / "requirements.txt").write_text(
        ORIGINAL_REQUIREMENTS, encoding="utf-8"
    )

    # 2. test_calculator.py — restore from git
    subprocess.run(
        ["git", "checkout", "HEAD", "--", "tests/test_calculator.py"],
        capture_output=True
    )

    # 3. ci.yml — restore from git
    subprocess.run(
        ["git", "checkout", "HEAD", "--", ".github/workflows/ci.yml"],
        capture_output=True
    )

    # 4. Group 1 source/fixture files — restore from git (they may have
    #    been modified by the injection or by a fix applied by the agent)
    if GROUP1_RESTORE_PATHS:
        subprocess.run(
            ["git", "checkout", "HEAD", "--", *GROUP1_RESTORE_PATHS],
            capture_output=True
        )

    # 5. Remove any unauthorized test file
    tests_dir = repo_root / "tests"
    if tests_dir.exists():
        for f in tests_dir.rglob("*.py"):
            if f.name not in ALLOWED_TEST_FILES:
                f.unlink()
                log.debug(f"Removed spurious test file: {f.name}")


def resolve_test_target_file(error: dict, repo_root: Path):
    """
    Determines the actual test file to modify for a 'test' case,
    reading the path from the synthetic ci_logs (same pattern used by
    agent.agents.test_agent.find_test_file).
    Returns None if no recognizable path appears in the logs.
    """
    import re
    match = re.search(r'(?:FAILED|ERROR)\s+(tests/[\w./]+\.py)', error.get("ci_logs", ""))
    if not match:
        return None
    return repo_root / match.group(1)


def _inject_test_generic(target: "Path", diff: str) -> bool:
    """Generic injection: line-by-line find/replace (same pattern as 'config')."""
    if not target.exists():
        return False
    content = target.read_text(encoding="utf-8")
    removed = [l[1:].strip() for l in diff.splitlines() if l.startswith("-")]
    added   = [l[1:].strip() for l in diff.splitlines() if l.startswith("+")]
    changed = False
    for old, new in zip(removed, added):
        if old and old in content:
            content = content.replace(old, new, 1)
            changed = True
    if changed:
        target.write_text(content, encoding="utf-8")
    return changed


def _inject_test_023(repo_root: Path) -> bool:
    """
    test_023: the case's git_diff describes a file move
    (app/services/payment.py -> app/billing/payment.py), not a diff of
    code lines — the generic find/replace does not apply. The baseline
    of tests/test_payment.py already imports from the correct path (app.billing.payment,
    consistent with expected_fix); the injection rewrites the import to the old path
    to reproduce the ModuleNotFoundError described in the case.
    """
    target = repo_root / "tests/test_payment.py"
    if not target.exists():
        return False
    content = target.read_text(encoding="utf-8")
    new_content = content.replace(
        "from app.billing.payment import", "from app.services.payment import"
    )
    if new_content == content:
        return False
    target.write_text(new_content, encoding="utf-8")
    return True


def _inject_test_027(repo_root: Path) -> bool:
    """
    test_027: the git_diff describes the removal of a fixture file from the
    commit, not a line diff — the injection deletes the fixture file
    to reproduce the FileNotFoundError described in the case.
    """
    fixture = repo_root / "tests/fixtures/sample.json"
    if not fixture.exists():
        return False
    fixture.unlink()
    return True


def _inject_test_010(repo_root: Path) -> bool:
    """
    test_010: the git_diff shows only one added line (no paired removed
    line) — the generic find/replace based on zip(removed,
    added) produces nothing. The baseline of tests/test_api.py is already in
    the correct state (the assert includes 'price'); the injection removes the
    'price' key from the assert to reproduce the mismatch with the actual dict
    returned by create_item (which always includes it).
    """
    target = repo_root / "tests/test_api.py"
    if not target.exists():
        return False
    content = target.read_text(encoding="utf-8")
    new_content = content.replace(
        '{"id": 1, "name": "item", "price": 10.0}',
        '{"id": 1, "name": "item"}',
    )
    if new_content == content:
        return False
    target.write_text(new_content, encoding="utf-8")
    return True


def _inject_test_012(repo_root: Path) -> bool:
    """
    test_012: the original diff shows the addition of 'commit=True' (a
    parameter WITH a default), which would never break an existing
    save(record) call — it does not reproduce the "missing required argument"
    error described in the ci_logs. Custom injection: makes 'commit' a required
    positional argument (no default), consistent with the actually observed error.
    """
    target = repo_root / "src/db.py"
    if not target.exists():
        return False
    content = target.read_text(encoding="utf-8")
    new_content = content.replace(
        "def save(self, record, commit=True):",
        "def save(self, record, commit):",
    )
    if new_content == content:
        return False
    target.write_text(new_content, encoding="utf-8")
    return True


def _inject_test_030(repo_root: Path) -> bool:
    """
    test_030: the git_diff describes the historical fix already applied to
    src/legacy.py (outside our control, it is already in the correct state
    in the baseline) — there is nothing to re-inject there. The actual broken
    element is an @pytest.mark.xfail(strict=True) marker left on the test
    after the bug was fixed: the injection adds it back, causing an
    XPASS(strict) that pytest treats as a failure.
    """
    target = repo_root / "tests/test_legacy.py"
    if not target.exists():
        return False
    content = target.read_text(encoding="utf-8")
    new_content = content.replace(
        "def test_old_behavior():",
        "@pytest.mark.xfail(strict=True)\ndef test_old_behavior():",
    )
    if new_content == content:
        return False
    target.write_text(new_content, encoding="utf-8")
    return True


def _inject_test_033(repo_root: Path) -> bool:
    """
    test_033: the git_diff has 3 removed lines and 2 added ones — the zip(removed,
    added) of the generic find/replace pairs only the first 2 and leaves
    the third removed line orphaned (direct mutation of CONFIG next to the
    now-undefined local variable 'config': it still breaks the test, but
    with a NameError instead of the intended behavior). Custom injection:
    replaces the whole test body with the direct mutation of the shared
    global state CONFIG, reproducing exactly the described scenario.
    """
    target = repo_root / "tests/test_settings.py"
    if not target.exists():
        return False
    content = target.read_text(encoding="utf-8")
    new_content = content.replace(
        "    config = copy.deepcopy(CONFIG)\n"
        "    config['env'] = 'production'\n"
        "    assert config['env'] == 'production'",
        "    CONFIG['env'] = 'production'\n"
        "    assert CONFIG['env'] == 'production'",
    )
    if new_content == content:
        return False
    target.write_text(new_content, encoding="utf-8")
    return True


def _inject_test_016(repo_root: Path) -> bool:
    """
    test_016: the fix replaces the whole line 'result = asyncio.run(fetch_data())'
    with a 4-line block (nested runner() function + call) — a number of
    removed/added lines that the generic find/replace cannot pair. Custom
    injection: introduces a runner() that calls loop.run_until_complete() while
    that same loop is already running (started by asyncio.run), deterministically
    reproducing "RuntimeError: This event loop is already running" (stdlib
    asyncio only, no dependency on pytest-asyncio).
    """
    target = repo_root / "tests/test_async.py"
    if not target.exists():
        return False
    content = target.read_text(encoding="utf-8")
    new_content = content.replace(
        "    result = asyncio.run(fetch_data())",
        "    async def runner():\n"
        "        loop = asyncio.get_event_loop()\n"
        "        return loop.run_until_complete(fetch_data())\n"
        "\n"
        "    result = asyncio.run(runner())",
    )
    if new_content == content:
        return False
    target.write_text(new_content, encoding="utf-8")
    return True


def _inject_test_047(repo_root: Path) -> bool:
    """
    test_047: composite case with two independent defects in the same file
    (assert with wrong tie-break order AND test_edge_case_empty_input function
    removed) — not expressible as a generic line-by-line find/replace.
    Custom injection: replaces the whole file content with the version
    that has both problems.
    """
    target = repo_root / "tests/test_recommender.py"
    if not target.exists():
        return False
    content = target.read_text(encoding="utf-8")
    broken = (
        "from src.recommender import recommend\n"
        "\n"
        "\n"
        "def test_ranking_order():\n"
        "    items = [{\"id\": \"c\", \"score\": 5}, {\"id\": \"a\", \"score\": 5}, {\"id\": \"b\", \"score\": 5}]\n"
        "    assert recommend(items) == [\"c\", \"a\", \"b\"]\n"
    )
    if content == broken:
        return False
    target.write_text(broken, encoding="utf-8")
    return True


SPECIAL_TEST_INJECTORS = {
    "test_010": _inject_test_010,
    "test_012": _inject_test_012,
    "test_023": _inject_test_023,
    "test_027": _inject_test_027,
    "test_030": _inject_test_030,
    "test_033": _inject_test_033,
    "test_016": _inject_test_016,
    "test_047": _inject_test_047,
}

# Cases in which the git_diff literally describes a line of SOURCE code
# (not of the test file) — the generic injection must be applied to the src/
# module listed here instead of the file resolved by resolve_test_target_file().
# All of these follow the standard convention "-"=correct state,
# "+"=state introduced by the upstream fix not reflected in the test (see the notes
# of each case in experiments/dataset.py).
TEST_TARGET_OVERRIDE = {
    "test_009": "src/services.py",
    "test_011": "src/auth.py",
    "test_013": "src/mailer.py",
    "test_014": "src/config.py",
    "test_015": "src/validator.py",
    "test_019": "src/serializer.py",
    "test_022": "src/parser.py",
    "test_040": "src/validation.py",
    "test_049": "src/logger.py",
}


def inject_error(error: dict) -> bool:
    """
    Introduces the specific error into the right file based on the category.
    Called after reset_files() for every test case.

    Returns True if the injection was applied successfully, False if no
    valid target file was found for the injection (e.g. the synthetic
    logs do not contain a recognizable path).
    """
    repo_root = Path(".")
    category  = error["category"]
    diff      = error.get("git_diff", "")
    error_id  = error["id"]

    if category == "dependency":
        current = (repo_root / "requirements.txt").read_text(encoding="utf-8")
        added   = [l[1:].strip() for l in diff.splitlines() if l.startswith("+")]
        for line in added:
            if line and line not in current:
                current += f"\n{line}"
        (repo_root / "requirements.txt").write_text(current, encoding="utf-8")
        return True

    elif category == "config":
        ci_path  = repo_root / ".github/workflows/ci.yml"
        content  = ci_path.read_text(encoding="utf-8")
        removed  = [l[1:].strip() for l in diff.splitlines() if l.startswith("-")]
        added    = [l[1:].strip() for l in diff.splitlines() if l.startswith("+")]
        for old, new in zip(removed, added):
            if old and old in content:
                content = content.replace(old, new, 1)
        ci_path.write_text(content, encoding="utf-8")
        return True

    elif category == "test":
        special = SPECIAL_TEST_INJECTORS.get(error_id)
        if special:
            return special(repo_root)
        override = TEST_TARGET_OVERRIDE.get(error_id)
        target = (repo_root / override) if override else resolve_test_target_file(error, repo_root)
        if target is None or not target.exists():
            log.warning(f"{error_id}: target file not found ({target}) — excluded from the Success Rate")
            return False
        return _inject_test_generic(target, diff)

    return False


# ══════════════════════════════════════════════════════════════
# REMOTE BRANCH CLEANUP — removes leftover "fix/ai-*" branches
# ══════════════════════════════════════════════════════════════

def cleanup_fix_branches(repo_name: str = "") -> int:
    """
    Deletes from the remote repository all the branches matching the pattern
    "fix/ai-*", created by fix_executor_node on every fix attempt
    (see agent/pipeline/fix_executor.py::build_branch_name). Without cleanup
    they accumulate on every benchmark run.

    Uses the GitHub instance already configured in the project (PyGitHub +
    GITHUB_TOKEN from .env, see agent/github/client.py::get_repo).

    Does not raise exceptions: a cleanup failure must not interrupt
    the benchmark. Returns the number of branches actually removed.
    """
    from agent.github.client import get_repo

    repo_name = repo_name or os.getenv("GITHUB_REPO", "")
    if not repo_name:
        log.warning("cleanup_fix_branches: GITHUB_REPO not configured — skip")
        return 0

    try:
        repo = get_repo(repo_name)
        targets = [b for b in repo.get_branches() if fnmatch.fnmatch(b.name, "fix/ai-*")]
    except Exception as e:
        log.warning(f"cleanup_fix_branches: unable to read the remote branches: {e}")
        return 0

    if not targets:
        log.info("cleanup_fix_branches: no 'fix/ai-*' branch to remove")
        return 0

    removed = 0
    for branch in targets:
        try:
            repo.get_git_ref(f"heads/{branch.name}").delete()
            removed += 1
        except Exception as e:
            log.warning(f"cleanup_fix_branches: unable to remove {branch.name}: {e}")
        time.sleep(0.5)  # rate limiting on the GitHub API

    log.info(f"cleanup_fix_branches: removed {removed}/{len(targets)} 'fix/ai-*' branches")
    return removed


# ══════════════════════════════════════════════════════════════
# STOP OLLAMA — frees VRAM between local models
# ══════════════════════════════════════════════════════════════

def stop_ollama_model(model_name: str):
    """Unloads the Ollama model from VRAM and waits for it to be released."""
    try:
        subprocess.run(
            ["ollama", "stop", model_name],
            capture_output=True, timeout=15
        )
        time.sleep(5)
        log.info(f"Ollama: model {model_name} unloaded from VRAM")
    except Exception as e:
        log.warning(f"Ollama stop failed for {model_name}: {e}")


# ══════════════════════════════════════════════════════════════
# TIMEOUT HANDLER — cross-platform (works on Windows)
# ══════════════════════════════════════════════════════════════

def run_with_timeout(func, args=(), timeout=300):
    """
    Runs func with a timeout using threading.
    Compatible with Windows, where signal.alarm is not available.
    """
    import threading

    result    = [None]
    exception = [None]

    def target():
        try:
            result[0] = func(*args)
        except Exception as e:
            exception[0] = e #type: ignore

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        raise TimeoutError(f"Timeout after {timeout}s")
    if exception[0]:
        raise exception[0]
    return result[0]


# ══════════════════════════════════════════════════════════════
# SINGLE ERROR EXECUTION
# ══════════════════════════════════════════════════════════════

def run_single_error(error: dict, dry_run: bool, no_memory: bool, readonly_memory: bool = False) -> dict:
    """
    Runs the system on a single dataset error.
    Returns a dictionary with all the metrics of the run.
    """
    # Lazy import to avoid reload issues
    from agent.graph import app

    state = {
        "ci_logs":          error["ci_logs"],
        "ci_job_name":      error["ci_job_name"],
        "ci_conclusion":    "failure",
        # opaque SHA1 of the case id: must NOT reveal the ground-truth category
        "commit_sha":       hashlib.sha1(error['id'].encode()).hexdigest(),
        # used only to tag/exclude episodes in memory; never part of an LLM prompt
        "case_id":          error['id'],
        "repo_name":        os.getenv("GITHUB_REPO", ""),
        "git_diff":         error.get("git_diff", ""),
        "repo_path":        ".",
        "attempt_number":   1,
        "attempts_history": [],
        # dry_run: skip the real CI → ci_fixed=True right away
        "ci_fixed":         True if dry_run else None,
        # no_memory / dry_run: skip ChromaDB saving
        "skip_memory":      no_memory or dry_run,
        # readonly_memory: RAG retrieval enabled but episode saving disabled
        # (only has an effect when memory is enabled, i.e. no_memory=False)
        "skip_memory_save": readonly_memory if not no_memory else False,
    }

    start_time = time.time()
    result     = app.invoke(state) #type: ignore
    elapsed    = round(time.time() - start_time, 2)

    # ── Extract metrics ──
    history      = result.get("attempts_history", [])
    final_status = result.get("final_status", "unknown")
    router_cat   = result.get("error_category", "unknown")
    router_conf  = result.get("error_confidence", 0.0) or 0.0
    router_reason= result.get("router_reasoning", "") or ""

    # Correct routing with respect to the dataset ground truth
    router_correct = 1 if router_cat == error["category"] else 0

    # Attempt at which it was fixed (1, 2 or 3) — None if escalated
    fix_attempt = len(history) if final_status == "fixed" and history else None

    # JSON parse failure: fallback triggered in the router
    json_parse_fail = 1 if (
        router_cat == "unknown" and
        router_conf == 0.0 and
        "Parsing failed" in router_reason
    ) else 0


    # Check in the reasoning or in the history whether memory was used
    memory_hits = 0
    for h in history:
        if h.get("memory_used"):  # field to be added in the agents
            memory_hits += 1

    return {
        "error_id":           error["id"],
        "category":           error["category"],
        "difficulty":         error["difficulty"],
        "final_status":       final_status,
        "success":            1 if final_status == "fixed" else 0,
        "router_category":    router_cat,
        "router_correct":     router_correct,
        "router_confidence":  round(router_conf, 3),
        "router_reasoning":   router_reason[:200],
        "attempts_count":     len(history),
        "fix_attempt":        fix_attempt,
        "json_parse_fail":    json_parse_fail,
        "latency_sec":        elapsed,
        "memory_hits":   memory_hits,   # how many times RAG found episodes
        "memory_active": 0 if no_memory else 1,  # experimental condition
    }


# ══════════════════════════════════════════════════════════════
# FULL MODEL EXECUTION
# ══════════════════════════════════════════════════════════════

def run_model(model: dict, errors: list, dry_run: bool, no_memory: bool,
              keep_branches: bool = False, readonly_memory: bool = False) -> list:
    """
    Runs all the errors on a specific model.
    Handles file reset, timeouts, pauses and VRAM release.
    """
    # Configure the provider for this model
    os.environ["LLM_PROVIDER"] = model["provider"]
    if model["provider"] == "ollama":
        os.environ["OLLAMA_MODEL"] = model.get("ollama_model", "llama31-4k")

    results = []
    total   = len(errors)
    timeout = model["timeout"]

    log.info(f"\n{'='*60}")
    log.info(f"MODEL: {model['name']} ({model['id']})")
    log.info(f"Errors: {total} | Timeout: {timeout}s | "
             f"dry-run: {dry_run} | no-memory: {no_memory}")
    log.info(f"{'='*60}")

    for i, error in enumerate(errors):
        log.info(
            f"\n[{i+1}/{total}] {error['id']} "
            f"({error['category']} / {error['difficulty']})"
        )

        # ── File reset before every test ──
        reset_files()

        # ── Inject the error into the file (only if not dry-run) ──
        if not dry_run:
            try:
                injected = inject_error(error)
                if not injected:
                    log.warning(f"{error['id']}: no target found for the injection — using synthetic logs")
            except Exception as e:
                log.warning(f"inject_error failed: {e} — using synthetic logs")

        # ── Default result row (for timeouts or errors) ──
        row = {
            "model_id":           model["id"],
            "model_name":         model["name"],
            "model_type":         model["type"],
            "dry_run":            1 if dry_run else 0,
            "no_memory":          1 if no_memory else 0,
            "error_id":           error["id"],
            "category":           error["category"],
            "difficulty":         error["difficulty"],
            "final_status":       "timeout",
            "success":            0,
            "router_category":    "",
            "router_correct":     0,
            "router_confidence":  0.0,
            "router_reasoning":   "",
            "attempts_count":     0,
            "fix_attempt":        None,
            "json_parse_fail":    0,
            "latency_sec":        float(timeout),
            "error_msg":          "",
        }

        try:
            run_result = run_with_timeout(
                run_single_error,
                args=(error, dry_run, no_memory, readonly_memory),
                timeout=timeout
            )
            # Merge
            row.update(run_result) #type: ignore
            row["error_msg"] = ""

            status_icon = "✅" if row["success"] else "❌"
            log.info(
                f"  {status_icon} {row['final_status']} | "
                f"router: {row['router_category']} "
                f"({row['router_confidence']:.0%}) | "
                f"attempts: {row['attempts_count']} | "
                f"{row['latency_sec']}s"
            )

        except TimeoutError:
            row["error_msg"] = "TIMEOUT"
            log.warning(f"  ⏰ TIMEOUT after {timeout}s")

        except Exception as e:
            row["final_status"] = "error"
            row["error_msg"]    = str(e)[:300]
            log.error(f"  💥 ERROR: {e}")

        results.append(row)

        # ── Pause between errors ──
        pause = 1 if model["provider"] in ("anthropic", "groq") else 2
        time.sleep(pause)

    # ── Free VRAM after a local model ──
    if model["provider"] == "ollama":
        stop_ollama_model(model.get("ollama_model", ""))
        time.sleep(8)  # generous pause between local models

    # ── Incremental cleanup of the "fix/ai-*" branches created by this model ──
    if not keep_branches:
        cleanup_fix_branches()

    return results


# ══════════════════════════════════════════════════════════════
# RESULTS SAVING
# ══════════════════════════════════════════════════════════════

def save_results(all_results: list, run_id: str):
    """Saves the results as CSV and JSON. Called after every model."""
    if not all_results:
        log.warning("No results to save")
        return None

    csv_path  = RESULTS_DIR / f"benchmark_{run_id}.csv"
    json_path = RESULTS_DIR / f"benchmark_{run_id}.json"

    fieldnames = list(all_results[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    log.info(f"Saved {len(all_results)} results → {csv_path.name}")
    return csv_path


# ══════════════════════════════════════════════════════════════
# TERMINAL SUMMARY
# ══════════════════════════════════════════════════════════════

def print_summary(all_results: list):
    """Prints summary tables to the terminal at the end of the benchmark."""
    if not all_results:
        return

    # Group by model
    by_model = {}
    for r in all_results:
        mid = r["model_id"]
        if mid not in by_model:
            by_model[mid] = []
        by_model[mid].append(r)

    print("\n" + "="*72)
    print("BENCHMARK SUMMARY — OVERALL SUCCESS RATE")
    print("="*72)
    print(f"{'Model':<30} {'SR%':>6} {'Router%':>8} {'AvgLat':>8} {'JSONfail':>9} {'N':>4}")
    print("-"*72)

    for mid, rows in by_model.items():
        n          = len(rows)
        sr         = sum(r["success"] for r in rows) / n * 100
        ra         = sum(r["router_correct"] for r in rows) / n * 100
        lat        = sum(r["latency_sec"] for r in rows) / n
        jf         = sum(r["json_parse_fail"] for r in rows)
        name       = rows[0]["model_name"]
        print(f"{name:<30} {sr:>5.1f}% {ra:>7.1f}% {lat:>7.1f}s {jf:>9} {n:>4}")

    print("\nSUCCESS RATE BY CATEGORY")
    print("="*72)
    cats = ["dependency", "test", "config"]
    print(f"{'Model':<30}" + "".join(f" {c[:6]:>9}" for c in cats))
    print("-"*60)

    for mid, rows in by_model.items():
        name = rows[0]["model_name"]
        line = f"{name:<30}"
        for cat in cats:
            sub = [r for r in rows if r["category"] == cat]
            sr  = sum(r["success"] for r in sub) / len(sub) * 100 if sub else -1
            line += f" {sr:>8.1f}%" if sr >= 0 else f" {'N/A':>9}"
        print(line)

    print("\nSUCCESS RATE BY DIFFICULTY")
    print("="*72)
    diffs = ["easy", "medium", "hard"]
    print(f"{'Model':<30}" + "".join(f" {d[:6]:>9}" for d in diffs))
    print("-"*60)

    for mid, rows in by_model.items():
        name = rows[0]["model_name"]
        line = f"{name:<30}"
        for diff in diffs:
            sub = [r for r in rows if r["difficulty"] == diff]
            sr  = sum(r["success"] for r in sub) / len(sub) * 100 if sub else -1
            line += f" {sr:>8.1f}%" if sr >= 0 else f" {'N/A':>9}"
        print(line)

    print("="*72)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Multi-model benchmark — Self-Healing CI"
    )
    parser.add_argument(
        "--provider",
        choices=["anthropic", "groq", "ollama", "openai", "all"],
        default="all",
        help="Provider LLM (default: all)"
    )
    parser.add_argument(
        "--ollama-model",
        dest="ollama_model",
        choices=["llama31-4k", "llama3.3:70b", "qwen38-4k",
                 "qwen3coder-4k", "mistral-4k", "all"],
        default="all",
        help="Specific Ollama model (use with --provider ollama)"
    )
    parser.add_argument(
        "--category",
        choices=["dependency", "test", "config", "all"],
        default="all",
        help="Error category (default: all)"
    )
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard", "all"],
        default="all",
        help="Error difficulty (default: all)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Router only, no real CI. Implies --no-memory."
    )
    parser.add_argument(
        "--no-memory",
        action="store_true",
        help="Disables saving to ChromaDB. "
             "Use for comparative benchmarks (identical conditions across models)."
    )
    parser.add_argument(
        "--clean-memory",
        action="store_true",
        help="Wipes ChromaDB before starting the benchmark."
    )
    parser.add_argument(
        "--readonly-memory",
        action="store_true",
        help="Enables RAG retrieval but disables episode saving. "
             "Use to test models against a pre-populated memory "
             "without polluting it.")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit to N errors per model (quick test)"
    )
    parser.add_argument(
        "--keep-branches",
        action="store_true",
        help="Disables the automatic cleanup of the 'fix/ai-*' branches on GitHub "
             "(useful for debugging)."
    )
    args = parser.parse_args()

    # dry-run implies no-memory
    if args.dry_run:
        args.no_memory = True

    # ── ChromaDB cleanup if requested ──
    if args.clean_memory:
        log.info("ChromaDB cleanup requested...")
        clean_chromadb()


    # ── Filter the dataset ──
    errors = DATASET
    if args.category != "all":
        errors = [e for e in errors if e["category"] == args.category]
    if args.difficulty != "all":
        errors = [e for e in errors if e["difficulty"] == args.difficulty]
    if args.limit:
        errors = errors[:args.limit]

    log.info(f"Dataset: {len(errors)} errors selected")

    # ── Filter the models ──
    models = MODELS
    if args.provider != "all":
        models = [m for m in models if m["provider"] == args.provider]
    if args.provider == "ollama" and args.ollama_model != "all":
        models = [m for m in models if m.get("ollama_model") == args.ollama_model]

    if not models:
        log.error("No model selected — check --provider and --ollama-model")
        sys.exit(1)

    log.info(f"Models: {[m['name'] for m in models]}")
    log.info(
        f"Mode: {'dry-run' if args.dry_run else 'full'} | "
        f"memory: {'OFF' if args.no_memory else 'ON'}"
    )

    # ── Run ID for the output files ──
    # Format: benchmark_{YYYYMMDD}_{HHMMSS}_{model_id}_{memory_condition}.csv
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.dry_run:
        memory_condition = "dryrun"
    elif args.no_memory:
        memory_condition = "nomemory"
    else:
        memory_condition = "memory"

    def build_run_id(model_id: str) -> str:
        return f"{timestamp}_{model_id}_{memory_condition}"

    # model_id "all_models" when the run covers more than one model
    # (e.g. --provider all, or --provider ollama --ollama-model all)
    final_model_id = "all_models" if len(models) > 1 else models[0]["id"]
    run_id = build_run_id(final_model_id)

    # ── Cleanup of "fix/ai-*" branches left over from previous runs ──
    if not args.keep_branches:
        log.info("Cleaning up 'fix/ai-*' branches left over from previous runs...")
        cleanup_fix_branches()
    else:
        log.info("--keep-branches enabled: skipping the cleanup of the 'fix/ai-*' branches")

    all_results = []

    for model in models:
        log.info(f"\n▶ Starting: {model['name']}")
        try:
            model_results = run_model(
                model, errors,
                dry_run=args.dry_run,
                no_memory=args.no_memory,
                keep_branches=args.keep_branches,
                readonly_memory=args.readonly_memory
            )
            all_results.extend(model_results)

            # Intermediate save after every model — separate CSV/JSON per
            # model (specific model_id, not the global run_id), so that a
            # benchmark interrupted halfway still leaves the per-model files.
            save_results(model_results, build_run_id(model["id"]))
            log.info(f"✓ {model['name']} completed — results saved")

            time.sleep(3)

        except KeyboardInterrupt:
            log.warning("Benchmark interrupted by the user (Ctrl+C)")
            break
        except Exception as e:
            log.error(f"Critical error on {model['name']}: {e}")
            continue

    # ── Final save and summary ──
    csv_path = save_results(all_results, run_id)
    print_summary(all_results)

    print(f"\n✅ Benchmark completed — {len(all_results)} total runs")
    if csv_path:
        print(f"📄 CSV: {csv_path}")
    print(f"📁 Results: {RESULTS_DIR}")


if __name__ == "__main__":
    main()