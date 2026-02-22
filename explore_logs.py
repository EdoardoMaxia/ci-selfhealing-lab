import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

g = Github(os.getenv("GITHUB_TOKEN"))
repo = g.get_repo(os.getenv("GITHUB_REPO"))

# Prendi l'ultima run della CI
runs = repo.get_workflow_runs()
last_run = runs[0]

print(f"Ultimo run: {last_run.name}")
print(f"Status: {last_run.status}")
print(f"Conclusione: {last_run.conclusion}")  # success / failure
print(f"Commit: {last_run.head_sha[:8]}")
print(f"Branch: {last_run.head_branch}")
print(f"URL logs: {last_run.logs_url}")

# Mostra i job falliti
print("\n--- JOB FALLITI ---")
for job in last_run.jobs():
    if job.conclusion == "failure":
        print(f"Job: {job.name}")
        for step in job.steps:
            if step.conclusion == "failure":
                print(f"  Step fallito: {step.name}")