from typing import TypedDict, Optional, List
from enum import Enum


class ErrorCategory(Enum):
    DEPENDENCY = "dependency"  # pip/npm broken, version conflict
    TEST = "test"            # assert failed, mock broken
    CONFIG = "config"        # YAML CI, env vars, Docker
    UNKNOWN = "unknown"      # non classificabile


class AgentState(TypedDict):
    # --- INPUT: dati dalla CI ---
    ci_logs: str               # log completo del job fallito
    ci_job_name: str           # nome del job (es. "Run Tests")
    ci_conclusion: str         # "failure" / "success"
    commit_sha: str            # sha del commit che ha triggerato il fallimento
    repo_name: str             # es. "username/ci-selfhealing-lab"
    git_diff: str              # diff dell'ultimo commit

    # --- ROUTING ---
    error_category: Optional[str]    # valorizzato dal Router Agent
    error_confidence: Optional[float] # 0.0 - 1.0
    router_reasoning: Optional[str]  # spiegazione della classificazione

    # --- FIX LOOP ---
    attempt_number: int              # tentativo corrente (1, 2, 3)
    fix_applied: Optional[str]       # descrizione del fix applicato
    fix_diff: Optional[str]          # diff delle modifiche apportate
    attempts_history: List[dict]     # storico di tutti i tentativi
    repo_path: str                   # path locale del repo
    ci_fixed: Optional[bool]         # True se la CI è verde dopo il fix

    # --- RAG ---
    skip_memory: Optional[bool]    # True → salta salvataggio ChromaDB

    # --- OUTPUT ---
    final_status: Optional[str]       # "fixed" / "escalated"
    explanation_report: Optional[str] # report in linguaggio naturale
    pr_url: Optional[str]             # URL della PR creata
    fix_branch: Optional[str]         # Nome del branch creato