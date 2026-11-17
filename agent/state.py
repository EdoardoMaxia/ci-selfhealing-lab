from typing import TypedDict, Optional, List
from enum import Enum

class ErrorCategory(Enum):
    DEPENDENCY = "dependency"  # pip/npm broken, version conflict
    TEST = "test"            # assert failed, mock broken
    CONFIG = "config"        # YAML CI, env vars, Docker
    UNKNOWN = "unknown"      # not classifiable


class AgentState(TypedDict):
    # --- INPUT: data from the CI ---
    ci_logs: str               # full log of the failed job
    ci_job_name: str           # job name (e.g. "Run Tests")
    ci_conclusion: str         # "failure" / "success"
    commit_sha: str            # sha of the commit that triggered the failure
    repo_name: str             # e.g. "username/ci-selfhealing-lab"
    git_diff: str              # diff of the last commit

    case_id: Optional[str]     # benchmark case id: ONLY for memory tagging/exclusion, never shown to LLMs

    # --- ROUTING ---
    error_category: Optional[str]    # set by the Router Agent
    error_confidence: Optional[float] # 0.0 - 1.0
    router_reasoning: Optional[str]  # explanation of the classification

    # --- FIX LOOP ---
    attempt_number: int              # current attempt (1, 2, 3)
    fix_applied: Optional[str]       # description of the applied fix
    fix_diff: Optional[str]          # diff of the changes made
    attempts_history: List[dict]     # history of all attempts
    repo_path: str                   # local path of the repo
    ci_fixed: Optional[bool]         # True if the CI is green after the fix
    modified_file: Optional[str]

    # --- PROTOCOL B (set only by `experiments/benchmark.py --test-protocol-b`; absent otherwise) ---
    fix_base_sha: Optional[str]       # commit holding the full failed state (pre-check, CI verified red):
                                      # the Fix Executor branches from it instead of clean main
    ci_runs: Optional[List[dict]]     # one record per Fix Executor attempt: branch, commit, run id, conclusion

    # --- RAG ---
    skip_memory: Optional[bool]    # True → skip ChromaDB saving
    skip_memory_save: Optional[bool]  # True → RAG retrieval enabled but episode saving disabled

    # --- OUTPUT ---
    final_status: Optional[str]       # "fixed" / "escalated"
    explanation_report: Optional[str] # natural-language report
    pr_url: Optional[str]             # URL of the created PR
    fix_branch: Optional[str]         # Name of the created branch