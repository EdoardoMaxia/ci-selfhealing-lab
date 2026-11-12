import os
import hmac
import hashlib
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from agent.pipeline.context_builder import build_state_from_payload

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("self-healing")

app = FastAPI(title="Self-Healing CI — Webhook Server")

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")


def verify_github_signature(payload_bytes: bytes, signature: str) -> bool:
    """
    Verifies the HMAC-SHA256 signature of the GitHub webhook.
    Prevents fraudulent requests from unauthorized sources.
    """
    # If the secret does not exist, block.
    if not WEBHOOK_SECRET:
        print("WARNING: Verification failed because WEBHOOK_SECRET is missing")
        return False
    
    # If GitHub did not send the signature, block.
    if not signature:
        return False

    # Compute and compare
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)



async def run_healing_pipeline(state: dict) -> None:
    """
    Runs the LangGraph graph in the background.
    """
    from agent.graph import app as graph_app
    import time

    repo = state.get("repo_name", "?")
    sha  = state.get("commit_sha", "?")[:8]
    log.info(f"🚀 Self-healing started — repo: {repo}, commit: {sha}")

    # Retry up to 3 times on transient API errors
    for attempt in range(3):
        try:
            result = graph_app.invoke(state) #type: ignore
            status = result.get("final_status", "unknown")
            pr_url = result.get("pr_url", "")
            if status == "fixed":
                log.info(f"✅ Fix completed — PR: {pr_url}")
            else:
                log.warning(f"🚨 Escalation after 3 attempts")
            return  # success, exit
        except Exception as e:
            if "500" in str(e) or "Internal server error" in str(e):
                log.warning(f"⚠️  Transient API error (attempt {attempt+1}/3) — retrying in 10s")
                time.sleep(10)
            else:
                log.error(f"❌ Pipeline error: {e}", exc_info=True)
                return  # non-transient error, do not retry
    log.error("❌ All retries failed — persistent API-side error")


@app.get("/")
async def health_check():
    """Health check — verifies that the server is up."""
    return {
        "status": "online",
        "service": "Self-Healing CI Webhook",
        "version": "1.0.0"
    }


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Main webhook endpoint.
    Receives GitHub Actions events and starts self-healing in the background.
    """
    # 1. Read the raw body for signature verification
    payload_bytes = await request.body()
    signature     = request.headers.get("X-Hub-Signature-256", "")

    # 2. Verify the authenticity of the request
    if not verify_github_signature(payload_bytes, signature):
        log.warning("⚠️  Invalid webhook signature — request rejected")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 3. Parse the payload
    payload = await request.json()
    event   = request.headers.get("X-GitHub-Event", "")

    # 4. Filter: only workflow_run with conclusion failure
    if event != "workflow_run":
        return {"status": "ignored", "reason": f"event={event}"}

    run        = payload.get("workflow_run", {})
    action     = payload.get("action", "")
    conclusion = run.get("conclusion", "")

    if action != "completed" or conclusion != "failure":
        return {"status": "ignored", "reason": f"action={action}, conclusion={conclusion}"}

    # 5. Avoid processing fix/** branches (the system's own fixes)
    branch = run.get("head_branch", "")
    if branch.startswith("fix/"):
        return {"status": "ignored", "reason": "fix branch — skip"}

    run_id = run["id"]
    sha    = run["head_sha"]
    repo   = payload["repository"]["full_name"]
    log.info(f"📥 Webhook received — repo: {repo}, sha: {sha[:8]}, run: {run_id}")

    # 6. Build the state and start healing in the background
    state = await build_state_from_payload(payload)
    background_tasks.add_task(run_healing_pipeline, state)

    # 7. Respond to GitHub immediately (within 10s)
    return {
        "status":  "healing_started",
        "run_id":  run_id,
        "repo":    repo,
        "commit":  sha[:8],
    }