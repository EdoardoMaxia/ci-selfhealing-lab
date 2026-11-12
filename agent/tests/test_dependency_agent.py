from dotenv import load_dotenv
load_dotenv()

from agent.graph import app


# Simulate a real dependency error
state = {
    "ci_logs": """
    ERROR: Could not find a version that satisfies the requirement numpy==99.99.99
    ERROR: No matching distribution found for numpy==99.99.99
    note: This error originates from a subprocess, and is likely not a problem with pip.
    pip install failed with exit code 1
    """,
    "ci_job_name":    "Install dependencies",
    "ci_conclusion":  "failure",
    "commit_sha":     "abc12345",
    "repo_name":      "anonymous/ci-selfhealing-lab",
    "git_diff":       "+numpy==99.99.99",
    "repo_path":      ".",  # current folder = "repo"
    "attempt_number": 1,
    "attempts_history": [],
    "ci_fixed":       True,  # simulate a green CI on the first attempt
}

print("🚀 Starting the self-healing system...\n")
result = app.invoke(state) #type: ignore

print(f"\n{'='*50}")
print(f"📊 Final result: {result['final_status']}")
print(f"🔧 Applied fix: {result.get('fix_applied', 'none')}")
print(f"📝 Diff:\n{result.get('fix_diff', 'none')}")




# ==================================================================
# ==================================================================
# ==================================================================
#           TEST 2: CI ALWAYS BROKEN


print("\n\n" + "="*50)
print("🧪 TEST 2: CI always broken → escalation after 3 attempts")
print("="*50 + "\n")

state_retry = {
    "ci_logs": """
    ERROR: Cannot install numpy==1.24.0 and pandas==2.0.0 because these
    package versions have conflicting dependencies.
    The conflict is caused by:
        pandas 2.0.0 depends on numpy>=1.23.2
        scipy 1.9.0 depends on numpy<1.25.0,>=1.18.5
    Could not find a version that satisfies all requirements.
    """,
    "ci_job_name":      "Install dependencies",
    "ci_conclusion":    "failure",
    "commit_sha":       "xyz99999",
    "repo_name":        "anonymous/ci-selfhealing-lab",
    "git_diff":         "+pandas==2.0.0",
    "repo_path":        ".",
    "attempt_number":   1,
    "attempts_history": [],
    "ci_fixed":         False,
}

result2 = app.invoke(state_retry) #type: ignore
print(f"\n📊 Final result: {result2['final_status']}")
print(f"📋 Attempts made: {len(result2['attempts_history'])}")
for h in result2['attempts_history']:
    print(f"   Attempt {h['attempt']}: {h['fix_applied'][:60]}")