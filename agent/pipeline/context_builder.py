import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


async def get_failed_job_logs(repo: str, run_id: int) -> tuple[str, str]:
    """
    Recupera i log e il nome del primo job fallito nella run.
    Ritorna (job_name, logs).
    """
    async with httpx.AsyncClient() as client:
        # Lista dei job nella run
        resp = await client.get(
            f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs",
            headers=HEADERS
        )
        jobs = resp.json().get("jobs", [])

        # Trova il primo job fallito
        failed_job = next(
            (j for j in jobs if j.get("conclusion") == "failure"),
            None
        )
        if not failed_job:
            return ("unknown", "No failed job found")

        job_id   = failed_job["id"]
        job_name = failed_job["name"]

        # Recupera i log del job
        log_resp = await client.get(
            f"https://api.github.com/repos/{repo}/actions/jobs/{job_id}/logs",
            headers=HEADERS,
            follow_redirects=True
        )
        logs = log_resp.text[:8000]  # tronca per sicurezza
        return (job_name, logs)


async def get_commit_diff(repo: str, sha: str) -> str:
    """Recupera il diff dell'ultimo commit che ha triggerato il fallimento."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.github.com/repos/{repo}/commits/{sha}",
            headers={**HEADERS, "Accept": "application/vnd.github.diff"}
        )
        return resp.text[:3000]


async def build_state_from_payload(payload: dict) -> dict:
    """
    Traduce il payload del webhook GitHub in AgentState completo.
    Chiamata dal trigger FastAPI.
    """
    run     = payload["workflow_run"]
    repo    = payload["repository"]["full_name"]  # es. "user/repo"
    run_id  = run["id"]
    sha     = run["head_sha"]

    # Recupera log e diff in parallelo
    job_name, ci_logs = await get_failed_job_logs(repo, run_id)
    git_diff          = await get_commit_diff(repo, sha)

    return {
        "ci_logs":          ci_logs,
        "ci_job_name":      job_name,
        "ci_conclusion":    "failure",
        "commit_sha":       sha,
        "repo_name":        repo,
        "repo_path":        ".",
        "git_diff":         git_diff,
        "attempt_number":   1,
        "attempts_history": [],
    }