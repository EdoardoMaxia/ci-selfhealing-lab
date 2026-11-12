import os
import re
import json
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def strip_think_blocks(text: str) -> str:
    """
    Removes the <think>...</think> reasoning blocks that some models
    (e.g. Qwen3.8, Qwen3-Coder via Ollama) prepend to the actual answer.
    Must be called BEFORE any parsing (JSON or file content).
    """
    return THINK_BLOCK_RE.sub("", text).strip()

# ---- Model selection ----
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")  # Read from the .env variable, otherwise "anthropic"

def get_llm():
    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o", temperature=0)
    elif LLM_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0) #type: ignore
    elif LLM_PROVIDER == "ollama":
        from langchain_ollama import ChatOllama
        model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        return ChatOllama(model=model, temperature=0)
    elif LLM_PROVIDER == "groq":
        from langchain_groq import ChatGroq
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        return ChatGroq(model=model, temperature=0, api_key=os.getenv("GROQ_API_KEY")) #type: ignore
    else:
        raise ValueError(f"Unsupported provider: {LLM_PROVIDER}")



ROUTER_SYSTEM_PROMPT = """
You are a CI/CD and DevOps expert. Your task is to classify
the type of error of a CI pipeline by analyzing its logs.

Available categories:
- DEPENDENCY: library errors, failed pip install, ModuleNotFoundError,
  incompatible versions, ImportError, package not found
- TEST: failed tests, AssertionError, broken fixtures, mock issues,
  pytest failures, insufficient coverage
- CONFIG: YAML errors, missing environment variables, Docker issues,
  unconfigured secrets, syntax errors in the CI file
- UNKNOWN: not attributable to the previous categories

Respond EXCLUSIVELY with a valid JSON, without additional text:
{
  "category": "DEPENDENCY|TEST|CONFIG|UNKNOWN",
  "confidence": 0.0-1.0,
  "reasoning": "short explanation in English, max 2 lines"
}
"""


def router_node(state: dict) -> dict:
    """
    Router node: classifies the type of CI error using an LLM.
    Receives the State and returns the updates to apply.
    """
    llm = get_llm()

    # Prepare the context for the LLM
    user_message = f"""
        Analyze this CI error and classify it.

        **Failed job:** {state['ci_job_name']}
        **Conclusion:** {state['ci_conclusion']}
        **Commit SHA:** {state['commit_sha'][:8]}

        **CI log (last 100 lines):**
        ```
        {state['ci_logs'][-3000:]}
        ```

        **Git diff of the commit:**
        ```
        {state.get('git_diff', 'Not available')[:1500]}
        ```

        Classify the error by responding ONLY with the requested JSON.
    """

    messages = [
        SystemMessage(content=ROUTER_SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ]

    # Call the LLM
    response = llm.invoke(messages)
    raw = response.content.strip() #type: ignore

    # Remove any <think>...</think> blocks (Qwen3.8, Qwen3-Coder, ...)
    raw = strip_think_blocks(raw)

    # Clean the response (sometimes the LLM adds ```json ...```)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback if the JSON is malformed
        result = {"category": "UNKNOWN", "confidence": 0.0, "reasoning": "Parsing failed"}

    print(f"🧭 Router → {result['category']} (confidence: {result['confidence']:.0%})")
    print(f"   Reasoning: {result['reasoning']}")

    # Return the updates to the State
    return {
        "error_category": result["category"].lower(),
        "error_confidence": result["confidence"],
        "router_reasoning": result["reasoning"]
    }