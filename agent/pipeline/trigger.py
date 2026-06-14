import os
import hmac
import hashlib
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from agent.pipeline.context_builder import build_state_from_payload

load_dotenv()

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("self-healing")

app = FastAPI(title="Self-Healing CI — Webhook Server")

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")


def verify_github_signature(payload_bytes: bytes, signature: str) -> bool:
    """
    Verifica la firma HMAC-SHA256 del webhook GitHub.
    Previene richieste fraudolente da fonti non autorizzate.
    """
    # Se il segreto non esiste, blocca.
    if not WEBHOOK_SECRET:
        print("ATTENZIONE: Verifica fallita perchè WEBHOOK_SECRET è assente")
        return False
    
    # Se GitHub non ha inviato la firma, blocca.
    if not signature:
        return False

    # Calcolo e confronto
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)



async def run_healing_pipeline(state: dict) -> None:
    """
    Esegue il grafo LangGraph in background.
    """
    from agent.graph import app as graph_app
    import time

    repo = state.get("repo_name", "?")
    sha  = state.get("commit_sha", "?")[:8]
    log.info(f"🚀 Self-healing avviato — repo: {repo}, commit: {sha}")

    # Retry fino a 3 volte su errori transitori dell'API
    for attempt in range(3):
        try:
            result = graph_app.invoke(state) #type: ignore
            status = result.get("final_status", "unknown")
            pr_url = result.get("pr_url", "")
            if status == "fixed":
                log.info(f"✅ Fix completato — PR: {pr_url}")
            else:
                log.warning(f"🚨 Escalation dopo 3 tentativi")
            return  # successo, esci
        except Exception as e:
            if "500" in str(e) or "Internal server error" in str(e):
                log.warning(f"⚠️  API error transitorio (attempt {attempt+1}/3) — riprovo tra 10s")
                time.sleep(10)
            else:
                log.error(f"❌ Errore nel pipeline: {e}", exc_info=True)
                return  # errore non transitorio, non riprovare
    log.error("❌ Falliti tutti i retry — errore persistente lato API")


@app.get("/")
async def health_check():
    """Health check — verifica che il server sia attivo."""
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
    Endpoint principale del webhook.
    Riceve eventi GitHub Actions e avvia il self-healing in background.
    """
    # 1. Leggi il body raw per la verifica firma
    payload_bytes = await request.body()
    signature     = request.headers.get("X-Hub-Signature-256", "")

    # 2. Verifica autenticità della richiesta
    if not verify_github_signature(payload_bytes, signature):
        log.warning("⚠️  Firma webhook non valida — richiesta rifiutata")
        raise HTTPException(status_code=401, detail="Firma non valida")

    # 3. Parsa il payload
    payload = await request.json()
    event   = request.headers.get("X-GitHub-Event", "")

    # 4. Filtra: solo workflow_run con conclusion failure
    if event != "workflow_run":
        return {"status": "ignored", "reason": f"event={event}"}

    run        = payload.get("workflow_run", {})
    action     = payload.get("action", "")
    conclusion = run.get("conclusion", "")

    if action != "completed" or conclusion != "failure":
        return {"status": "ignored", "reason": f"action={action}, conclusion={conclusion}"}

    # 5. Evita di processare branch fix/** (fix del sistema stesso)
    branch = run.get("head_branch", "")
    if branch.startswith("fix/"):
        return {"status": "ignored", "reason": "fix branch — skip"}

    run_id = run["id"]
    sha    = run["head_sha"]
    repo   = payload["repository"]["full_name"]
    log.info(f"📥 Webhook ricevuto — repo: {repo}, sha: {sha[:8]}, run: {run_id}")

    # 6. Costruisce lo state e avvia l'healing in background
    state = await build_state_from_payload(payload)
    background_tasks.add_task(run_healing_pipeline, state)

    # 7. Risponde subito a GitHub (entro 10s)
    return {
        "status":  "healing_started",
        "run_id":  run_id,
        "repo":    repo,
        "commit":  sha[:8],
    }