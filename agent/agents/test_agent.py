import os
import re
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from agent.agents.router import get_llm, strip_think_blocks

from agent.memory.episodic_store import (
    retrieve_similar_episodes,
    format_episodes_for_prompt
)

load_dotenv()


TEST_SYSTEM_PROMPT = """
You are an expert in Python testing with pytest.
Your task is to analyze a failed test and propose the correct fix.

CRITICAL RULE: you must distinguish between two scenarios:
1. The TEST is wrong (assert with wrong value, outdated mock) → fix the test
2. The SOURCE CODE is wrong → fix the source code

In both cases, respond with the COMPLETE and CORRECT content of the file
to modify. Respond ONLY with the file content, without markdown or explanations.

Strategies per attempt:
- Attempt 1: minimal fix — change only the line causing the failure
- Attempt 2: contextual fix — also update related tests or the setup
- Attempt 3: approach different from the previous ones — consider rewriting the test
"""


def read_file(path: str) -> str:
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else ""


def write_file(path: str, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")
    print(f"✍️  File updated: {path}")


def compute_diff(original: str, updated: str) -> str:
    orig  = original.strip().splitlines()
    new   = updated.strip().splitlines()
    lines = []
    for l in orig:
        if l not in new: lines.append(f"- {l}")
    for l in new:
        if l not in orig: lines.append(f"+ {l}")
    return "\n".join(lines) if lines else "(no changes)"


def find_test_file(ci_logs: str, repo_path: str) -> str:
    """
    Extracts the test file path from the pytest logs.
    E.g.: 'FAILED tests/test_calculator.py::test_add' → 'tests/test_calculator.py'
    """
    match = re.search(r'FAILED\s+([\w/\\]+\.py)', ci_logs)
    if match:
        rel_path = match.group(1).replace("\\", "/")
        return str(Path(repo_path) / rel_path).replace(os.sep, "/")
    # Fallback: look for any .py file in the logs
    match2 = re.search(r'(tests/[\w]+\.py)', ci_logs)
    if match2:
        return str(Path(repo_path) / match2.group(1)).replace(os.sep, "/")
    return str(Path(repo_path) / "tests/test_calculator.py").replace(os.sep, "/")


def test_agent_node(state: dict) -> dict:
    llm       = get_llm()
    attempt   = state.get("attempt_number", 1)
    repo_path = state.get("repo_path", ".")
    history   = state.get("attempts_history", [])

    print(f"\n🧪 Test Agent — Attempt {attempt}/3")

    # Locate the test file from the logs
    test_file  = find_test_file(state["ci_logs"], repo_path)
    test_code  = read_file(test_file)

    # Also read the source code for context
    src_file   = str(Path(repo_path) / "src/calculator.py")
    src_code   = read_file(src_file)

    similar = []

    # Strategy per attempt
    if attempt == 1:
        attempt_context = "MINIMAL fix: correct only the line causing the failure."
    elif attempt == 2:
        prev = history[-1]["fix_applied"] if history else "none"
        attempt_context = f"The previous attempt ({prev}) failed. BROADER fix: also update the related tests."
    else:
        # Retrieve similar fixes from the episodic memory
        similar = retrieve_similar_episodes(
            error_logs=state["ci_logs"],
            category="test",
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

        **CI log (pytest error):**
        ```
        {state['ci_logs'][-2000:]}
        ```

        **Current content of the test file ({test_file}):**
        ```python
        {test_code}
        ```

        **Source code (for context):**
        ```python
        {src_code}
        ```

        **Git diff of the commit:**
        ```
        {state.get('git_diff', 'N/A')}
        ```

        Generate the COMPLETE and CORRECT content of the test file.
        Respond ONLY with the Python code, without backticks or explanations.
    """

    response    = llm.invoke([
        SystemMessage(content=TEST_SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ])
    new_content = response.content.strip() #type: ignore

    # Remove any <think>...</think> blocks (Qwen3.8, Qwen3-Coder, ...)
    new_content = strip_think_blocks(new_content)

    # Clean up leftover backticks
    if new_content.startswith("```"):
        lines = new_content.split("\n")
        new_content = "\n".join(lines[1:-1])


    diff = compute_diff(test_code, new_content)
    print(f"   Changes:\n{diff}")

    write_file(test_file, new_content)

    # Also save the path of the modified file in the state
    new_history = history + [{
        "attempt":     attempt,
        "agent":       "test",
        "fix_applied": f"test file updated (attempt {attempt})",
        "fix_diff":    diff,
        "file_path":   test_file,
        "memory_used": len(similar) > 0,
        "memory_hits": len(similar),
    }]

    return {
        "fix_applied":      f"Test fix attempt {attempt}: {diff[:80]}",
        "fix_diff":         diff,
        "modified_file":    test_file,
        "attempt_number":   attempt + 1,
        "attempts_history": new_history,
    }