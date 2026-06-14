from dotenv import load_dotenv
load_dotenv()

from agent.graph import app

# Recupera il commit SHA dell'ultimo push
import subprocess
sha = subprocess.check_output(
    ["git", "rev-parse", "HEAD"]
).decode().strip()

print(f"🔍 Commit SHA: {sha[:8]}")

state = {
    "ci_logs": """
    ERROR: Could not find a version that satisfies the requirement numpy==99.99.99
    ERROR: No matching distribution found for numpy==99.99.99
    pip install failed with exit code 1
    """,

    "ci_job_name":     "Install dependencies",
    "ci_conclusion":   "failure",
    "commit_sha":      sha,
    "repo_name":       "EdoardoMaxia/ci-selfhealing-lab",
    "git_diff":        "+numpy==99.99.99",
    "repo_path":       ".",
    "attempt_number":  1,
    "attempts_history": [],
}

print("\n🚀 Self-healing avviato — operazioni reali su GitHub\n")
result = app.invoke(state) #type: ignore

print(f"\n{'='*50}")
print(f"📊 Risultato: {result['final_status']}")
if result.get("pr_url"):
    print(f"📬 PR: {result['pr_url']}")