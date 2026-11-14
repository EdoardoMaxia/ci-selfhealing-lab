"""
API smoke test: one tiny call per provider, through the SAME get_llm() the Router
and the specialist agents use (same model names, temperature and API keys).
Run it before an expensive benchmark / dry-run to fail fast on bad keys or models.

Usage (from the repo root):
    python experiments/check_api.py                       # anthropic + openai
    python experiments/check_api.py --providers anthropic
    python experiments/check_api.py --providers ollama --ollama-model llama31-4k
    python experiments/check_api.py --providers github      # GITHUB_TOKEN / GITHUB_REPO used by the Fix Executor

Exit code is 0 only if every requested provider answered.
The API keys are never printed (only whether they are set).
"""
import os
import sys
import time
import argparse
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent))

KEY_VARS = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "groq": "GROQ_API_KEY"}


def check(provider: str, ollama_model: str) -> bool:
    key_var = KEY_VARS.get(provider)
    key_info = f"{key_var} {'set' if os.getenv(key_var) else 'NOT SET'}" if key_var else "no API key needed"
    print(f"\n=== {provider} ({key_info}) ===")
    os.environ["LLM_PROVIDER"] = provider
    if provider == "ollama":
        os.environ["OLLAMA_MODEL"] = ollama_model
    try:
        import agent.agents.router as router
        router.LLM_PROVIDER = provider            # module global is read at import time
        llm = router.get_llm()
        model = getattr(llm, "model", None) or getattr(llm, "model_name", None)
        start = time.time()
        resp = llm.invoke("Reply with the single word: OK")
        elapsed = time.time() - start
        text = str(resp.content).strip().replace("\n", " ")[:80]
        usage = getattr(resp, "usage_metadata", None)
        print(f"  model:   {model}\n  reply:   {text!r}\n  latency: {elapsed:.2f}s\n  usage:   {usage}")
        print("  RESULT:  OK")
        return True
    except Exception as e:                        # bad key, unknown model, network, missing package, ...
        print(f"  RESULT:  FAILED  {type(e).__name__}: {str(e)[:200]}")
        return False


def check_github() -> bool:
    """The benchmark opens branches/commits/PRs on GITHUB_REPO with GITHUB_TOKEN (Fix Executor):
    a bad token makes every case fail with 401 although the LLM calls work."""
    print(f"\n=== github (GITHUB_TOKEN {'set' if os.getenv('GITHUB_TOKEN') else 'NOT SET'}, "
          f"GITHUB_REPO {os.getenv('GITHUB_REPO') or 'NOT SET'}) ===")
    try:
        from agent.github.client import get_repo
        repo = get_repo(os.getenv("GITHUB_REPO", ""))
        perms = getattr(repo, "permissions", None)
        print(f"  repo:    {repo.full_name}\n  push:    {getattr(perms, 'push', 'unknown')}")
        if perms is not None and not perms.push:
            print("  RESULT:  FAILED  token has no push permission on the repo")
            return False
        print("  RESULT:  OK")
        return True
    except Exception as e:
        print(f"  RESULT:  FAILED  {type(e).__name__}: {str(e)[:200]}")
        return False


def main():
    ap = argparse.ArgumentParser(description="API smoke test through the project's get_llm()")
    ap.add_argument("--providers", nargs="+", default=["anthropic", "openai"],
                    choices=["anthropic", "openai", "groq", "ollama", "github"])
    ap.add_argument("--ollama-model", default="llama31-4k")
    args = ap.parse_args()
    results = {p: (check_github() if p == "github" else check(p, args.ollama_model)) for p in args.providers}
    print("\nSummary:", ", ".join(f"{p}={'OK' if ok else 'FAILED'}" for p, ok in results.items()))
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
