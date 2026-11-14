from dotenv import load_dotenv
load_dotenv()  # must be the first thing executed

from agent.graph import app

from pathlib import Path

def reset_test_files():
    """Restores the files to their 'broken' state before each test."""
    # requirements.txt with a dependency error
    Path("requirements.txt").write_text(
        "pytest==7.4.0\npytest-cov==4.1.0\nnumpy==99.99.99\n",
        encoding="utf-8"
    )
    # test_calculator.py with a wrong assert
    content = Path("tests/test_calculator.py").read_text(encoding="utf-8")
    content = content.replace("assert add(2, 3) == 5", "assert add(2, 3) == 99")
    Path("tests/test_calculator.py").write_text(content, encoding="utf-8")




# --- Error 1: Broken dependency ---
state_dep = {
    "ci_logs": """
        ERROR: Could not find a version that satisfies the requirement numpy==99.99.99
        ERROR: No matching distribution found for numpy==99.99.99
        pip install failed with exit code 1
    """,
    "ci_job_name": "Install dependencies",
    "ci_conclusion": "failure",
    "commit_sha": "abc12345",
    "repo_name": "anonymous/ci-selfhealing-lab",
    "git_diff": "+numpy==99.99.99",
    "attempt_number": 1,
    "attempts_history": []
}

# --- Error 2: Broken test ---
state_test = {
    "ci_logs": """
        FAILED tests/test_calculator.py::test_add_positive - AssertionError: assert 5 == 99
        short test summary info: FAILED tests/test_calculator.py::test_add_positive
        1 failed, 5 passed in 0.42s
    """,
    "ci_job_name": "Run Tests",
    "ci_conclusion": "failure",
    "commit_sha": "def67890",
    "repo_name": "anonymous/ci-selfhealing-lab",
    "git_diff": "-assert add(2, 3) == 5\n+assert add(2, 3) == 99",
    "attempt_number": 1,
    "attempts_history": []
}

# --- Error 3: Broken config ---
state_conf = {
    "ci_logs": """
        Error: Version 3.99 with arch x64 not found
        The version '3.99' with architecture 'x64' was not found
        Available versions: 3.8, 3.9, 3.10, 3.11, 3.12
    """,
    "ci_job_name": "Set up Python 3.99",
    "ci_conclusion": "failure",
    "commit_sha": "ghi11223",
    "repo_name": "anonymous/ci-selfhealing-lab",
    "git_diff": "-python-version: '3.11'\n+python-version: '3.99'",
    "attempt_number": 1,
    "attempts_history": []
}


# --- Error 4: NONSENSE TO TEST ESCALATE ---
state_escalate = {
    "ci_logs": """
        DARTH VADER WILL CONQUER THE ENTIRE GALAXY.
        BEWARE, EARTHLINGS!!!
    """,
    "ci_job_name": "bugsssss",
    "ci_conclusion": "failure",
    "commit_sha": "ghi11229",
    "repo_name": "anonymous/ci-selfhealing-lab",
    "git_diff": "????",
    "attempt_number": 1,
    "attempts_history": []
}


# Test the 3 cases
for name, state in [("DEPENDENCY", state_dep), ("TEST", state_test), ("CONFIG", state_conf), ("ESCALATE", state_escalate)]:
    print(f"\n{'='*50}")
    print(f"🧪 Test error: {name}")
    print("="*50)
    reset_test_files()
    result = app.invoke(state) #type: ignore
    print(f"✅ Final result: {result['final_status']}")