"""

Il Fix Executor è il nodo LangGraph che orchestra tutto:
- legge il file modificato dall'agente;
- lo carica su GitHub;
- aspetta la CI e aggiorna lo state con il risultato reale.

"""

import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from agent.github.client import (
    get_repo, create_branch, commit_file,
    wait_for_ci, create_pull_request
)


load_dotenv()


# File che ogni agente può modificare
AGENT_FILE_MAP = {
    "dependency" : "requirements.txt",
    "test" :       "tests/test_calculator.py",
    "config" :     ".github/workflows/ci.yml"
}



def build_branch_name(state: dict) -> str:
    """Genera un nome branch univoco per il fix."""
    category = state.get("error_category", "unknown")
    sha_short = state.get("commit_sha", "xxxxx")[:7]
    attempt = state.get("attempt_number", 1) - 1 # -1 perchè già incrementato
    timestamp = datetime.now().strftime("%H%M%S")
    return f"fix/ai-{category}-{sha_short}-t{attempt}-{timestamp}"



def build_pr_body(state: dict) -> str:
    """Genera il corpo della PR con il report completo."""
    history = state.get("attempts_history", [])

    history_text = "\n".join([
        f"- **Tentativo {h['attempt']}**: {h['fix_applied']}\n  ```diff\n  {h['fix_diff']}\n  ```"
        for h in history
    ])

    return f"""## 🤖 Self-Healing CI — Fix Automatico

    ### Errore rilevato
    - **Categoria**: `{state.get('error_category', 'unknown')}`
    - **Job fallito**: `{state.get('ci_job_name', 'N/A')}`
    - **Commit**: `{state.get('commit_sha', 'N/A')[:8]}`
    - **Confidence classificazione**: {state.get('error_confidence', 0):.0%}

    ### Ragionamento del Router
    {state.get('router_reasoning', 'N/A')}

    ### Fix applicati
    {history_text}

    ### Note
    - Fix generato automaticamente dal sistema Self-Healing CI
    - Verificato: CI verde ✅ dopo l'applicazione
    - Richiede review umana prima del merge

    > *Generato da Self-Healing CI Agent — Tesi LM-32*
    """



def fix_executor_node(state: dict) -> dict:
    """
    Nodo Fix Executor: dopo che un agente ha modificato il file localmente,
    questo nodo lo carica su GitHub, aspetta la CI e aggiorna lo state.
    """
    repo_name = state.get("repo_name")
    repo_path = state.get("repo_path", ".")
    category  = state.get("error_category", "dependency")

    print(f"\n🔧 Fix Executor avviato per categoria: {category}")

    # 1. Individua quale file è stato modificato
    if category == "test" and state.get("modified_file"):
        file_path = state["modified_file"]
        # Converti path assoluto in relativo al repo
        file_path = file_path.replace(str(Path(repo_path).resolve()), "").lstrip("/\\")
    else:
        file_path = AGENT_FILE_MAP.get(category, "requirements.txt")
        
    local_file = Path(repo_path) / file_path

    if not local_file.exists():
        print(f"⚠️  File {file_path} non trovato localmente")
        return {"ci_fixed": False}

    new_content = local_file.read_text(encoding="utf-8")

    # 2. Connettiti al repo GitHub
    repo       = get_repo(repo_name) #type: ignore
    main_sha   = repo.get_branch("main").commit.sha
    branch_name = build_branch_name(state)

    # 3. Crea il branch e fai il commit
    create_branch(repo, main_sha, branch_name)
    commit_message = (
        f"fix(ai): auto-fix {category} error\n\n"
        f"Commit originale: {state.get('commit_sha','')[:8]}\n"
        f"Tentativo: {state.get('attempt_number', 1) - 1}/3\n"
        f"[self-healing-ci]"
    )
    commit_file(repo, branch_name, file_path, new_content, commit_message)

    # 4. Aspetta il risultato della CI
    ci_passed = wait_for_ci(repo, branch_name, timeout_sec=300)

    # 5. Aggiorna lo state con il risultato reale
    updates = {"ci_fixed": ci_passed, "fix_branch": branch_name}

    if ci_passed:
        # CI verde: la PR verrà creata dal nodo create_pr
        updates["fix_branch"] = branch_name
        print("✅ CI verde — pronto per la PR")
    else:
        print("❌ CI ancora rossa")

    return updates