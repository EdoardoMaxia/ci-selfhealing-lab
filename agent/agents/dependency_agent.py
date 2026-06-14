import os
import re
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from agent.memory.episodic_store import (
    retrieve_similar_episodes,
    format_episodes_for_prompt
)

load_dotenv()


# Riusa la stessa funzione get_llm del router
from agent.agents.router import get_llm

# ─────────────────────────────────────────────
#  SYSTEM PROMPT — specializzato su dipendenze
# ─────────────────────────────────────────────
DEPENDENCY_SYSTEM_PROMPT = """
Sei un esperto di gestione delle dipendenze Python.
Il tuo compito è analizzare un errore di dipendenza in una CI pipeline
e generare il contenuto CORRETTO e COMPLETO del file requirements.txt.

Regole:
1. Analizza i log per capire QUALE dipendenza ha causato il fallimento
2. Usa il contenuto attuale del requirements.txt come base
3. Genera il file requirements.txt corretto e completo
4. Rispondi SOLO con il contenuto del file, senza spiegazioni né markdown

Strategie per tentativo:
- Tentativo 1: pin della versione corretta (es. numpy==1.24.0)
- Tentativo 2: aggiorna il gruppo di dipendenze correlate
- Tentativo 3: usa fix simili dal contesto storico fornito
"""


def read_requirements(repo_path: str) -> str:    
    """Legge il requirements.txt dal repo locale."""
    req_path = Path(repo_path) / "requirements.txt"
    if req_path.exists():
        return req_path.read_text(encoding="utf-8")
    return ""



def write_requirements(repo_path: str, content: str) -> None:
    """Scrive il nuovo requirements.txt sul disco."""
    req_path = Path(repo_path) / "requirements.txt"
    req_path.write_text(content, encoding="utf-8")
    print(f"✍️  requirements.txt aggiornato in {req_path}")



def compute_diff(original: str, updated: str) -> str:
    """Diff riga per riga, preserva l'ordine."""
    orig_lines = original.strip().splitlines()
    new_lines  = updated.strip().splitlines()

    diff_lines = []
    for line in orig_lines:
        if line not in new_lines:
            diff_lines.append(f"- {line}")
    for line in new_lines:
        if line not in orig_lines:
            diff_lines.append(f"+ {line}")

    return "\n".join(diff_lines) if diff_lines else "(nessuna modifica rilevata)"


def dependency_agent_node(state: dict) -> dict:
    """
    Nodo Dependency Agent: genera e applica un fix al requirements.txt.
    """

    llm = get_llm()
    attempt = state.get("attempt_number", 1)
    repo_path = state.get("repo_path", ".")
    history = state.get("attempts_history", [])

    print(f"\n📦 Dependency Agent — Tentativo {attempt}/3")

    # Legge il requirements.txt attuale
    current_requirements = read_requirements(repo_path)

    # Costruisce il contesto in base al tentativo
    attempt_context = ""
    similar = []
    if attempt == 1:
        attempt_context = "Applica un fix CONSERVATIVO: pinna solo la versione della dipendenza rotta."
    elif attempt == 2:
        prev = history[-1]["fix_applied"] if history else "nessuno"
        attempt_context = f""" Il tentativo precedente ha fallito: {prev}
        Applica un fix PIU AMPIO: aggiorna tutte le dipendenze correlate al problema."""
    elif attempt == 3:
        # Recupera fix simili dalla memoria episodica
        similar = retrieve_similar_episodes(
            error_logs=state["ci_logs"],
            category="dependency",
            top_k=3
        )
        memory_context = format_episodes_for_prompt(similar)

        prev_list = "\n".join([f"- {h['fix_applied']}" for h in history])
        attempt_context = f"""I tentativi precedenti hanno fallito:
            {prev_list}

            {memory_context}

            Usa le informazioni dalla memoria per proporre un fix diverso dai precedenti."""

        if similar:
            print(f"   🧠 Memoria: trovati {len(similar)} episodi simili")
    

    # Messaggio all'LLM
    user_message = f"""
        **Strategia per questo tentativo:** {attempt_context}

        **Log CI con l'errore:**
        ```
        {state['ci_logs'][-2000:]}
        ```

        **requirements.txt attuale:**
        ```
        {current_requirements}
        ```

        **Git diff del commit che ha causato il fallimento:**
        ```
        {state.get('git_diff', 'Non disponibile')}
        ```

        Genera il contenuto COMPLETO e CORRETTO del nuovo requirements.txt.
        Rispondi SOLO con il contenuto del file, senza backtick né spiegazioni.  
    """

    messages = [
        SystemMessage(content=DEPENDENCY_SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ]

    # Chiama l'LLM
    response = llm.invoke(messages)
    new_content = response.content.strip() #type: ignore


    # Pulisce eventuali backtick residui
    if new_content.startswith("```"):
        lines = new_content.split("\n")
        new_content = "\n".join(lines[1:-1])


    # Calcola il diff per il report
    diff = compute_diff(current_requirements, new_content)
    print(f"    Modifiche:\n{diff}")


    # Applica il fix sul disco
    write_requirements(repo_path, new_content)

    # Aggiorna lo storico dei tentativi
    new_history = history + [{
        "attempt":     attempt,
        "agent":       "dependency",
        "fix_applied": f"requirements.txt aggiornato (tentativo {attempt})",
        "fix_diff":    diff,
        "memory_used": len(similar) > 0,
        "memory_hits": len(similar),
    }]    

    return {
        "fix_applied":      f"Dependency fix tentativo {attempt}: {diff[:100]}",
        "fix_diff":         diff,
        "attempt_number":   attempt + 1,
        "attempts_history": new_history,
    }