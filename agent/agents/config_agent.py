from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from agent.agents.router import get_llm, strip_think_blocks

from agent.memory.episodic_store import (
    retrieve_similar_episodes,
    format_episodes_for_prompt
)

load_dotenv()


CONFIG_SYSTEM_PROMPT = """
Sei un esperto di GitHub Actions e CI/CD pipelines.
Il tuo compito è analizzare un errore nel file .github/workflows/ci.yml
e generare il contenuto CORRETTO e COMPLETO del file.

Conoscenze chiave:
- Versioni Python valide per actions/setup-python: 3.8, 3.9, 3.10, 3.11, 3.12
- Versioni actions raccomandate: actions/checkout@v4, actions/setup-python@v5
- Il file YAML deve avere indentazione a 2 spazi, mai tab
- I job devono avere almeno: runs-on, steps con checkout e setup

Rispondi SOLO con il contenuto YAML del file, senza backtick né spiegazioni.

Strategie per tentativo:
- Tentativo 1: fix minimale — correggi solo la riga problematica
- Tentativo 2: fix strutturale — rivedi l'intera sezione con l'errore
- Tentativo 3: riscrivi il job completo con configurazione standard
"""


def read_yaml(repo_path: str) -> str:
    p = Path(repo_path) / ".github/workflows/ci.yml"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def write_yaml(repo_path: str, content: str) -> None:
    p = Path(repo_path) / ".github/workflows/ci.yml"
    p.write_text(content, encoding="utf-8")
    print(f"✍️  ci.yml aggiornato")


def compute_diff(original: str, updated: str) -> str:
    orig  = original.strip().splitlines()
    new   = updated.strip().splitlines()
    lines = []
    for l in orig:
        if l not in new: lines.append(f"- {l}")
    for l in new:
        if l not in orig: lines.append(f"+ {l}")
    return "\n".join(lines) if lines else "(nessuna modifica)"


def config_agent_node(state: dict) -> dict:
    llm       = get_llm()
    attempt   = state.get("attempt_number", 1)
    repo_path = state.get("repo_path", ".")
    history   = state.get("attempts_history", [])

    print(f"\n⚙️  Config Agent — Tentativo {attempt}/3")

    current_yaml = read_yaml(repo_path)

    similar = []
    if attempt == 1:
        attempt_context = "Fix MINIMALE: correggi solo la riga che causa il fallimento."
    elif attempt == 2:
        prev = history[-1]["fix_applied"] if history else "nessuno"
        attempt_context = f"Tentativo precedente ({prev}) fallito. Rivedi l'intera sezione."
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

        **Log CI (errore):**
        ```
        {state['ci_logs'][-2000:]}
        ```

        **Contenuto attuale di .github/workflows/ci.yml:**
        ```yaml
        {current_yaml}
        ```

        **Git diff del commit:**
        ```
        {state.get('git_diff', 'N/A')}
        ```

        Genera il contenuto COMPLETO e CORRETTO del file ci.yml.
        Rispondi SOLO con il YAML, senza backtick né spiegazioni.
    """

    response    = llm.invoke([
        SystemMessage(content=CONFIG_SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ])
    new_content = response.content.strip() #type: ignore

    # Rimuove eventuali blocchi <think>...</think> (Qwen3.8, Qwen3-Coder, ...)
    new_content = strip_think_blocks(new_content)

    # Pulisce backtick e header ```yaml
    if new_content.startswith("```"):
        lines = new_content.split("\n")
        new_content = "\n".join(lines[1:-1])


    diff = compute_diff(current_yaml, new_content)
    print(f"   Modifiche:\n{diff}")

    write_yaml(repo_path, new_content)

    new_history = history + [{
        "attempt":     attempt,
        "agent":       "config",
        "fix_applied": f"ci.yml aggiornato (tentativo {attempt})",
        "fix_diff":    diff,
        "file_path":   ".github/workflows/ci.yml",
        "memory_used": len(similar) > 0,
        "memory_hits": len(similar),
    }]

    return {
        "fix_applied":      f"Config fix tentativo {attempt}: {diff[:80]}",
        "fix_diff":         diff,
        "attempt_number":   attempt + 1,
        "attempts_history": new_history,
    }