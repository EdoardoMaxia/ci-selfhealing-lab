from dotenv import load_dotenv
load_dotenv()  # deve essere la prima cosa eseguita

from agent.graph import app

from pathlib import Path

def reset_test_files():
    """Ripristina i file al loro stato 'rotto' prima di ogni test."""
    # requirements.txt con errore dependency
    Path("requirements.txt").write_text(
        "pytest==7.4.0\npytest-cov==4.1.0\nnumpy==99.99.99\n",
        encoding="utf-8"
    )
    # test_calculator.py con assert sbagliato
    content = Path("tests/test_calculator.py").read_text(encoding="utf-8")
    content = content.replace("assert add(2, 3) == 5", "assert add(2, 3) == 99")
    Path("tests/test_calculator.py").write_text(content, encoding="utf-8")




# --- Errore 1: Dipendenza rotta ---
state_dep = {
    "ci_logs": """
        ERROR: Could not find a version that satisfies the requirement numpy==99.99.99
        ERROR: No matching distribution found for numpy==99.99.99
        pip install failed with exit code 1
    """,
    "ci_job_name": "Install dependencies",
    "ci_conclusion": "failure",
    "commit_sha": "abc12345",
    "repo_name": "EdoardoMaxia/ci-selfhealing-lab",
    "git_diff": "+numpy==99.99.99",
    "attempt_number": 1,
    "attempts_history": []
}

# --- Errore 2: Test rotto ---
state_test = {
    "ci_logs": """
        FAILED tests/test_calculator.py::test_add_positivi - AssertionError: assert 5 == 99
        short test summary info: FAILED tests/test_calculator.py::test_add_positivi
        1 failed, 5 passed in 0.42s
    """,
    "ci_job_name": "Run Tests",
    "ci_conclusion": "failure",
    "commit_sha": "def67890",
    "repo_name": "EdoardoMaxia/ci-selfhealing-lab",
    "git_diff": "-assert add(2, 3) == 5\n+assert add(2, 3) == 99",
    "attempt_number": 1,
    "attempts_history": []
}

# --- Errore 3: Config rotta ---
state_conf = {
    "ci_logs": """
        Error: Version 3.99 with arch x64 not found
        The version '3.99' with architecture 'x64' was not found
        Available versions: 3.8, 3.9, 3.10, 3.11, 3.12
    """,
    "ci_job_name": "Set up Python 3.99",
    "ci_conclusion": "failure",
    "commit_sha": "ghi11223",
    "repo_name": "EdoardoMaxia/ci-selfhealing-lab",
    "git_diff": "-python-version: '3.11'\n+python-version: '3.99'",
    "attempt_number": 1,
    "attempts_history": []
}


# --- Errore 4: SENZA SENSO PER TESTARE ESCALATE ---
state_escalate = {
    "ci_logs": """
        DARTH VADER CONQUISTERA' L'INTERA GALASSIA.
        ATTENTI TERRESTRI!!!
    """,
    "ci_job_name": "bugsssss",
    "ci_conclusion": "failure",
    "commit_sha": "ghi11229",
    "repo_name": "EdoardoMaxia/ci-selfhealing-lab",
    "git_diff": "????",
    "attempt_number": 1,
    "attempts_history": []
}


# Testa i 3 casi
for name, state in [("DIPENDENZA", state_dep), ("TEST", state_test), ("CONFIG", state_conf), ("ESCALATE", state_escalate)]:
    print(f"\n{'='*50}")
    print(f"🧪 Test errore: {name}")
    print("="*50)
    reset_test_files()
    result = app.invoke(state) #type: ignore
    print(f"✅ Risultato finale: {result['final_status']}")