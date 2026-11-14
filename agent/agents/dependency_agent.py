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


# Reuse the same get_llm function as the router
from agent.agents.router import get_llm, strip_think_blocks

# ─────────────────────────────────────────────
#  SYSTEM PROMPT — specialized in dependencies
# ─────────────────────────────────────────────
DEPENDENCY_SYSTEM_PROMPT = """
You are an expert in Python dependency management.
Your task is to analyze a dependency error in a CI pipeline
and generate the CORRECT and COMPLETE content of the requirements.txt file.

Rules:
1. Analyze the logs to understand WHICH dependency caused the failure
2. Use the current content of requirements.txt as the base
3. Generate the correct and complete requirements.txt file
4. Respond ONLY with the file content, without explanations or markdown

Strategies per attempt:
- Attempt 1: pin the correct version (e.g. numpy==1.24.0)
- Attempt 2: update the group of related dependencies
- Attempt 3: use similar fixes from the provided historical context
"""


def read_requirements(repo_path: str) -> str:    
    """Reads requirements.txt from the local repo."""
    req_path = Path(repo_path) / "requirements.txt"
    if req_path.exists():
        return req_path.read_text(encoding="utf-8")
    return ""



def write_requirements(repo_path: str, content: str) -> None:
    """Writes the new requirements.txt to disk."""
    req_path = Path(repo_path) / "requirements.txt"
    req_path.write_text(content, encoding="utf-8")
    print(f"✍️  requirements.txt updated in {req_path}")



def compute_diff(original: str, updated: str) -> str:
    """Line-by-line diff, preserves ordering."""
    orig_lines = original.strip().splitlines()
    new_lines  = updated.strip().splitlines()

    diff_lines = []
    for line in orig_lines:
        if line not in new_lines:
            diff_lines.append(f"- {line}")
    for line in new_lines:
        if line not in orig_lines:
            diff_lines.append(f"+ {line}")

    return "\n".join(diff_lines) if diff_lines else "(no changes detected)"


def dependency_agent_node(state: dict) -> dict:
    """
    Dependency Agent node: generates and applies a fix to requirements.txt.
    """

    llm = get_llm()
    attempt = state.get("attempt_number", 1)
    repo_path = state.get("repo_path", ".")
    history = state.get("attempts_history", [])

    print(f"\n📦 Dependency Agent — Attempt {attempt}/3")

    # Read the current requirements.txt
    current_requirements = read_requirements(repo_path)

    # Build the context based on the attempt
    attempt_context = ""
    similar = []
    if attempt == 1:
        attempt_context = "Apply a CONSERVATIVE fix: pin only the version of the broken dependency."
    elif attempt == 2:
        prev = history[-1]["fix_applied"] if history else "none"
        attempt_context = f""" The previous attempt failed: {prev}
        Apply a BROADER fix: update all the dependencies related to the problem."""
    elif attempt == 3:
        # Retrieve similar fixes from the episodic memory
        similar = retrieve_similar_episodes(
            error_logs=state["ci_logs"],
            category="dependency",
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
    

    # Message to the LLM
    user_message = f"""
        **Strategy for this attempt:** {attempt_context}

        **CI log with the error:**
        ```
        {state['ci_logs'][-2000:]}
        ```

        **Current requirements.txt:**
        ```
        {current_requirements}
        ```

        **Git diff of the commit that caused the failure:**
        ```
        {state.get('git_diff', 'Not available')}
        ```

        Generate the COMPLETE and CORRECT content of the new requirements.txt.
        Respond ONLY with the file content, without backticks or explanations.  
    """

    messages = [
        SystemMessage(content=DEPENDENCY_SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ]

    # Call the LLM
    response = llm.invoke(messages)
    new_content = response.content.strip() #type: ignore

    # Remove any <think>...</think> blocks (Qwen3.8, Qwen3-Coder, ...)
    new_content = strip_think_blocks(new_content)

    # Clean up any leftover backticks
    if new_content.startswith("```"):
        lines = new_content.split("\n")
        new_content = "\n".join(lines[1:-1])


    # Compute the diff for the report
    diff = compute_diff(current_requirements, new_content)
    print(f"    Changes:\n{diff}")


    # Apply the fix on disk
    write_requirements(repo_path, new_content)

    # Update the attempt history
    new_history = history + [{
        "attempt":     attempt,
        "agent":       "dependency",
        "fix_applied": f"requirements.txt updated (attempt {attempt})",
        "fix_diff":    diff,
        "memory_used": len(similar) > 0,
        "memory_hits": len(similar),
    }]    

    return {
        "fix_applied":      f"Dependency fix attempt {attempt}: {diff[:100]}",
        "fix_diff":         diff,
        "attempt_number":   attempt + 1,
        "attempts_history": new_history,
    }