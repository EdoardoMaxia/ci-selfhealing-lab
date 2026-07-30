import os
import re
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from agent.agents.router import get_llm

from agent.memory.episodic_store import (
    retrieve_similar_episodes,
    format_episodes_for_prompt
)

load_dotenv()


TEST_SYSTEM_PROMPT = """
Sei un esperto di testing Python con pytest.
Il tuo compito è analizzare un test fallito e proporre il fix corretto.

REGOLA CRITICA: devi distinguere due scenari:
1. Il TEST è sbagliato (assert con valore errato, mock non aggiornato) → fix il test
2. Il CODICE SORGENTE è sbagliato → fix il codice sorgente

In entrambi i casi, rispondi con il contenuto COMPLETO e CORRETTO del file
da modificare. Rispondi SOLO con il contenuto del file, senza markdown né spiegazioni.

Strategie per tentativo:
- Tentativo 1: fix minimale — cambia solo la riga che causa il fallimento
- Tentativo 2: fix contestuale — aggiorna anche i test correlati o il setup
- Tentativo 3: approccio diverso dai precedenti — considera di riscrivere il test
"""


def read_file(path: str) -> str:
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else ""


def write_file(path: str, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")
    print(f"✍️  File aggiornato: {path}")


def compute_diff(original: str, updated: str) -> str:
    orig  = original.strip().splitlines()
    new   = updated.strip().splitlines()
    lines = []
    for l in orig:
        if l not in new: lines.append(f"- {l}")
    for l in new:
        if l not in orig: lines.append(f"+ {l}")
    return "\n".join(lines) if lines else "(nessuna modifica)"


def find_test_file(ci_logs: str, repo_path: str) -> str:
    """
    Estrae il path del file di test dai log pytest.
    Es: 'FAILED tests/test_calculator.py::test_add' → 'tests/test_calculator.py'
    """
    match = re.search(r'FAILED\s+([\w/\\]+\.py)', ci_logs)
    if match:
        rel_path = match.group(1).replace("\\", "/")
        return str(Path(repo_path) / rel_path).replace(os.sep, "/")
    # Fallback: cerca qualsiasi file .py nei log
    match2 = re.search(r'(tests/[\w]+\.py)', ci_logs)
    if match2:
        return str(Path(repo_path) / match2.group(1)).replace(os.sep, "/")
    return str(Path(repo_path) / "tests/test_calculator.py").replace(os.sep, "/")


def test_agent_node(state: dict) -> dict:
    llm       = get_llm()
    attempt   = state.get("attempt_number", 1)
    repo_path = state.get("repo_path", ".")
    history   = state.get("attempts_history", [])

    print(f"\n🧪 Test Agent — Tentativo {attempt}/3")

    # Individua il file di test dai log
    test_file  = find_test_file(state["ci_logs"], repo_path)
    test_code  = read_file(test_file)

    # Legge anche il codice sorgente per contesto
    src_file   = str(Path(repo_path) / "src/calculator.py")
    src_code   = read_file(src_file)

    similar = []

    # Strategia per tentativo
    if attempt == 1:
        attempt_context = "Fix MINIMALE: correggi solo la riga che causa il fallimento."
    elif attempt == 2:
        prev = history[-1]["fix_applied"] if history else "nessuno"
        attempt_context = f"Il tentativo precedente ({prev}) ha fallito. Fix PIÙ AMPIO: aggiorna anche i test correlati."
    else:
        # Recupera fix simili dalla memoria episodica
        similar = retrieve_similar_episodes(
            error_logs=state["ci_logs"],
            category="config",
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

    user_message = f"""
        **Strategia:** {attempt_context}

        **Log CI (errore pytest):**
        ```
        {state['ci_logs'][-2000:]}
        ```

        **Contenuto attuale del file di test ({test_file}):**
        ```python
        {test_code}
        ```

        **Codice sorgente (per contesto):**
        ```python
        {src_code}
        ```

        **Git diff del commit:**
        ```
        {state.get('git_diff', 'N/A')}
        ```

        Genera il contenuto COMPLETO e CORRETTO del file di test.
        Rispondi SOLO con il codice Python, senza backtick né spiegazioni.
    """

    response    = llm.invoke([
        SystemMessage(content=TEST_SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ])
    new_content = response.content.strip() #type: ignore

    # Pulisce backtick residui
    if new_content.startswith("```"):
        lines = new_content.split("\n")
        new_content = "\n".join(lines[1:-1])


    diff = compute_diff(test_code, new_content)
    print(f"   Modifiche:\n{diff}")

    write_file(test_file, new_content)

    # Salva anche il path del file modificato nello state
    new_history = history + [{
        "attempt":     attempt,
        "agent":       "test",
        "fix_applied": f"test file aggiornato (tentativo {attempt})",
        "fix_diff":    diff,
        "file_path":   test_file,
        "memory_used": len(similar) > 0,
        "memory_hits": len(similar),
    }]

    return {
        "fix_applied":      f"Test fix tentativo {attempt}: {diff[:80]}",
        "fix_diff":         diff,
        "modified_file":    test_file,
        "attempt_number":   attempt + 1,
        "attempts_history": new_history,
    }