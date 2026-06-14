from dotenv import load_dotenv
load_dotenv()
from agent.graph import app

state = {
    "ci_logs": """
    FAILED tests/test_calculator.py::test_add_positivi - AssertionError: assert 5 == 99
    short test summary info
    FAILED tests/test_calculator.py::test_add_positivi
    1 failed, 5 passed in 0.42s
    """,
    "ci_job_name":     "Run Tests",
    "ci_conclusion":   "failure",
    "commit_sha":      "testsha1",
    "repo_name":       "EdoardoMaxia/ci-selfhealing-lab",
    "git_diff":        "-assert add(2, 3) == 5\n+assert add(2, 3) == 99",
    "repo_path":       ".",
    "attempt_number":  1,
    "attempts_history": [],
    "ci_fixed":        False,
}

result = app.invoke(state) #type: ignore
print(f"\n📊 Risultato: {result['final_status']}")
if result.get("pr_url"):
    print(f"📬 PR: {result['pr_url']}")