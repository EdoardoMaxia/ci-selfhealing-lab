from dotenv import load_dotenv
load_dotenv()
from agent.graph import app

state = {
    "ci_logs": """
    Error: Version 3.99 with arch x64 not found
    The version '3.99' with architecture 'x64' was not found
    Available versions: 3.8, 3.9, 3.10, 3.11, 3.12
    """,
    "ci_job_name":     "Set up Python 3.99",
    "ci_conclusion":   "failure",
    "commit_sha":      "confsha1",
    "repo_name":       "EdoardoMaxia/ci-selfhealing-lab",
    "git_diff":        "-python-version: '3.11'\n+python-version: '3.99'",
    "repo_path":       ".",
    "attempt_number":  1,
    "attempts_history": [],
    "ci_fixed":        False,
}

result = app.invoke(state) #type: ignore
print(f"\n📊 Risultato: {result['final_status']}")
if result.get("pr_url"):
    print(f"📬 PR: {result['pr_url']}")