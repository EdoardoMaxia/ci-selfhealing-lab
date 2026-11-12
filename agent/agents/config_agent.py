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
You are an expert in GitHub Actions and CI/CD pipelines.
Your task is to analyze an error in the .github/workflows/ci.yml file
and generate the CORRECT and COMPLETE content of the file.

Key knowledge:
- Valid Python versions for actions/setup-python: 3.8, 3.9, 3.10, 3.11, 3.12
- Recommended action versions: actions/checkout@v4, actions/setup-python@v5
- The YAML file must use 2-space indentation, never tabs
- Jobs must have at least: runs-on, steps with checkout and setup

Respond ONLY with the YAML content of the file, without backticks or explanations.

Strategies per attempt:
- Attempt 1: minimal fix — correct only the problematic line
- Attempt 2: structural fix — review the whole section containing the error
- Attempt 3: rewrite the complete job with a standard configuration
"""


def read_yaml(repo_path: str) -> str:
    p = Path(repo_path) / ".github/workflows/ci.yml"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def write_yaml(repo_path: str, content: str) -> None:
    p = Path(repo_path) / ".github/workflows/ci.yml"
    p.write_text(content, encoding="utf-8")
    print(f"✍️  ci.yml updated")


def compute_diff(original: str, updated: str) -> str:
    orig  = original.strip().splitlines()
    new   = updated.strip().splitlines()
    lines = []
    for l in orig:
        if l not in new: lines.append(f"- {l}")
    for l in new:
        if l not in orig: lines.append(f"+ {l}")
    return "\n".join(lines) if lines else "(no changes)"


def config_agent_node(state: dict) -> dict:
    llm       = get_llm()
    attempt   = state.get("attempt_number", 1)
    repo_path = state.get("repo_path", ".")
    history   = state.get("attempts_history", [])

    print(f"\n⚙️  Config Agent — Attempt {attempt}/3")

    current_yaml = read_yaml(repo_path)

    similar = []
    if attempt == 1:
        attempt_context = "MINIMAL fix: correct only the line causing the failure."
    elif attempt == 2:
        prev = history[-1]["fix_applied"] if history else "none"
        attempt_context = f"Previous attempt ({prev}) failed. Review the whole section."
    else:
        # Retrieve similar fixes from the episodic memory
        similar = retrieve_similar_episodes(
            error_logs=state["ci_logs"],
            category="config",
            top_k=3,
            current_case_id=state.get("case_id"),  # never retrieve the episode of the SAME case
        )
        memory_context = format_episodes_for_prompt(similar)

        prev_list = "\n".join([f"- {h['fix_applied']}" for h in history])
        attempt_context = f"""The previous attempts failed:
            {prev_list}

            {memory_context}

            Use the information from memory to propose a fix different from the previous ones."""

        if similar:
            print(f"   🧠 Memory: found {len(similar)} similar episodes")

    user_message = f"""
        **Strategy:** {attempt_context}

        **CI log (error):**
        ```
        {state['ci_logs'][-2000:]}
        ```

        **Current content of .github/workflows/ci.yml:**
        ```yaml
        {current_yaml}
        ```

        **Git diff of the commit:**
        ```
        {state.get('git_diff', 'N/A')}
        ```

        Generate the COMPLETE and CORRECT content of the ci.yml file.
        Respond ONLY with the YAML, without backticks or explanations.
    """

    response    = llm.invoke([
        SystemMessage(content=CONFIG_SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ])
    new_content = response.content.strip() #type: ignore

    # Remove any <think>...</think> blocks (Qwen3.8, Qwen3-Coder, ...)
    new_content = strip_think_blocks(new_content)

    # Clean up backticks and the ```yaml header
    if new_content.startswith("```"):
        lines = new_content.split("\n")
        new_content = "\n".join(lines[1:-1])


    diff = compute_diff(current_yaml, new_content)
    print(f"   Changes:\n{diff}")

    write_yaml(repo_path, new_content)

    new_history = history + [{
        "attempt":     attempt,
        "agent":       "config",
        "fix_applied": f"ci.yml updated (attempt {attempt})",
        "fix_diff":    diff,
        "file_path":   ".github/workflows/ci.yml",
        "memory_used": len(similar) > 0,
        "memory_hits": len(similar),
    }]

    return {
        "fix_applied":      f"Config fix attempt {attempt}: {diff[:80]}",
        "fix_diff":         diff,
        "attempt_number":   attempt + 1,
        "attempts_history": new_history,
    }