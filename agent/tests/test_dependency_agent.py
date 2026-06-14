from dotenv import load_dotenv
load_dotenv()

from agent.graph import app


# Simula un errore di dipendenza reale
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
    "repo_name":      "EdoardoMaxia/ci-selfhealing-lab",
    "git_diff":       "+numpy==99.99.99",
    "repo_path":      ".",  # cartella corrente = "repo"
    "attempt_number": 1,
    "attempts_history": [],
    "ci_fixed":       True,  # simuliamo CI verde al primo tentativo
}

print("🚀 Avvio sistema self-healing...\n")
result = app.invoke(state) #type: ignore

print(f"\n{'='*50}")
print(f"📊 Risultato finale: {result['final_status']}")
print(f"🔧 Fix applicato: {result.get('fix_applied', 'nessuno')}")
print(f"📝 Diff:\n{result.get('fix_diff', 'nessuno')}")




# ==================================================================
# ==================================================================
# ==================================================================
#           TEST 2: CI SEMPRE ROTTA


print("\n\n" + "="*50)
print("🧪 TEST 2: CI sempre rotta → escalation dopo 3 tentativi")
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
    "repo_name":        "EdoardoMaxia/ci-selfhealing-lab",
    "git_diff":         "+pandas==2.0.0",
    "repo_path":        ".",
    "attempt_number":   1,
    "attempts_history": [],
    "ci_fixed":         False,
}

result2 = app.invoke(state_retry) #type: ignore
print(f"\n📊 Risultato finale: {result2['final_status']}")
print(f"📋 Tentativi effettuati: {len(result2['attempts_history'])}")
for h in result2['attempts_history']:
    print(f"   Tentativo {h['attempt']}: {h['fix_applied'][:60]}")