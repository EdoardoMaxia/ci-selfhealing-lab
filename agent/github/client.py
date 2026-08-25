import os
import time
import logging
from github import Github
from github.GithubException import GithubException, UnknownObjectException
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger("agent.github.client")

# Numero di tentativi e attesa tra un tentativo e l'altro per le chiamate
# alla Contents API subito dopo create_branch(): il nuovo ref può non essere
# ancora visibile per qualche secondo, sia in lettura (repo.get_contents)
# sia in scrittura (repo.update_file/create_file — l'endpoint
# "create-or-update-file-contents"), in modo indipendente: verificato che
# repo.get_contents() può avere successo al primo tentativo mentre il
# successivo repo.update_file() 404 comunque, quindi entrambe le operazioni
# vanno ritentate separatamente, non solo la lettura dello SHA.
GET_CONTENTS_RETRIES = 3
GET_CONTENTS_RETRY_DELAY_SEC = 2


def get_github_client():
    """Restituisce un client GitHub autenticato."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN non trovato nel .env")
    return Github(token)


def get_repo(repo_name: str):
    """Restituisce l'oggetto repo da PyGitHub"""
    g = get_github_client()
    return g.get_repo(repo_name)


def create_branch(repo, base_sha: str, branch_name: str) -> None:
    """Crea un nuovo branch a partire dal commit SHA specificato."""
    try:
        repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=base_sha,
        )
        print(f"🌿 Branch creato: {branch_name}")
    except Exception as e:
        if "Reference already exists" in str(e):
            print(f"🌿 Branch già esistente: {branch_name}")
        else:
            raise


def _get_contents_with_retry(repo, file_path: str, branch: str):
    """
    Recupera il contenuto/SHA di un file su un branch, con retry+backoff.

    Subito dopo create_branch(), il nuovo ref può non essere ancora visibile
    alla Contents API (repo.get_contents) anche se esiste già a livello Git
    Data API — GitHub propaga i due sottosistemi in modo asincrono. Senza
    retry questo si traduce in un 404 sistematico su commit_file() per i
    branch appena creati. Rilancia l'ultima UnknownObjectException se tutti
    i tentativi falliscono, così il chiamante può comunque distinguere
    "file non trovato" da altri errori.
    """
    def _call():
        return repo.get_contents(file_path, ref=branch)

    return _call_with_retry(_call, op_name="get_contents", file_path=file_path, branch=branch)


def _call_with_retry(func, *, op_name: str, file_path: str, branch: str):
    """
    Esegue func() ritentando fino a GET_CONTENTS_RETRIES volte se solleva
    UnknownObjectException (404), con attesa GET_CONTENTS_RETRY_DELAY_SEC tra
    un tentativo e l'altro. Usato sia per la lettura (get_contents) sia per
    la scrittura (update_file/create_file, l'endpoint
    "create-or-update-file-contents") perché entrambe possono restituire 404
    indipendentemente subito dopo create_branch(), per propagazione
    asincrona del nuovo ref lato GitHub. Rilancia l'ultima
    UnknownObjectException se tutti i tentativi falliscono.
    """
    last_exc = None
    for attempt in range(1, GET_CONTENTS_RETRIES + 1):
        log.info(
            f"{op_name}: path={file_path!r} ref={branch!r} "
            f"(tentativo {attempt}/{GET_CONTENTS_RETRIES})"
        )
        try:
            return func()
        except UnknownObjectException as e:
            last_exc = e
            if attempt < GET_CONTENTS_RETRIES:
                log.warning(
                    f"{op_name}: 404 su path={file_path!r} ref={branch!r} "
                    f"(tentativo {attempt}/{GET_CONTENTS_RETRIES}) — "
                    f"probabile propagazione asincrona del branch, "
                    f"retry tra {GET_CONTENTS_RETRY_DELAY_SEC}s"
                )
                time.sleep(GET_CONTENTS_RETRY_DELAY_SEC)
    raise last_exc


def commit_file(repo, branch: str, file_path: str,
                new_content: str, commit_message: str) -> None:
    """
    Commit di un singolo file su un branch esistente.
    Gestisce sia file nuovi che aggiornamenti.
    """
    # Normalizza il path per la Contents API di GitHub, che vuole sempre
    # forward slash (mai backslash — rilevante se file_path arriva da un
    # Path costruito con os.sep su Windows) e nessuno slash iniziale.
    normalized_path = file_path.replace("\\", "/").lstrip("/")
    if normalized_path != file_path:
        log.warning(f"commit_file: path normalizzato {file_path!r} -> {normalized_path!r}")
    file_path = normalized_path

    # 1. Recupera il file attuale per ottenere il suo SHA (necessario per
    #    update). Un 404 qui, anche dopo i retry, significa che il file non
    #    esiste ancora su questo branch -> va creato, non aggiornato.
    try:
        existing = _get_contents_with_retry(repo, file_path, branch)
    except UnknownObjectException as e:
        log.warning(
            f"create_file: path={file_path!r} branch={branch!r} — "
            f"file non trovato dopo {GET_CONTENTS_RETRIES} tentativi "
            f"(status={getattr(e, 'status', '?')})"
        )

        def _create():
            repo.create_file(
                path=file_path,
                message=commit_message,
                content=new_content,
                branch=branch
            )

        try:
            _call_with_retry(_create, op_name="create_file", file_path=file_path, branch=branch)
        except GithubException as e2:
            log.error(
                f"create_file fallito: path={file_path!r} branch={branch!r} "
                f"status={getattr(e2, 'status', '?')} data={getattr(e2, 'data', '?')}"
            )
            raise
        print(f"✍️  File creato: {file_path}")
        return
    except GithubException as e:
        log.error(
            f"get_contents fallito: path={file_path!r} branch={branch!r} "
            f"status={getattr(e, 'status', '?')} data={getattr(e, 'data', '?')}"
        )
        raise

    # 2. Il file esiste già su questo branch -> aggiornalo. update_file()
    #    (stesso endpoint "create-or-update-file-contents" di create_file())
    #    può a sua volta restituire 404 per propagazione asincrona del
    #    branch anche quando il get_contents precedente è già riuscito —
    #    va ritentato separatamente.
    log.info(f"update_file: path={file_path!r} branch={branch!r} sha={existing.sha}")

    def _update():
        repo.update_file(
            path=file_path,
            message=commit_message,
            content=new_content,
            sha=existing.sha,
            branch=branch
        )

    try:
        _call_with_retry(_update, op_name="update_file", file_path=file_path, branch=branch)
    except GithubException as e:
        log.error(
            f"update_file fallito: path={file_path!r} branch={branch!r} "
            f"status={getattr(e, 'status', '?')} data={getattr(e, 'data', '?')}"
        )
        raise
    print(f"✍️  File aggiornato: {file_path}")



def wait_for_ci(repo, branch: str,
                timeout_sec: int = 300,
                poll_interval: int = 15) -> bool:
    
    """
    Aspetta il completamento della CI sul branch specificato.
    Ritorna True se la CI è verde, False altrimenti.
    Timeout default: 5 minuti.
    """
    print(f"⏳ Attendo la CI sul branch '{branch}'...")
    elapsed = 0

    while elapsed < timeout_sec:
        try:
            runs = repo.get_workflow_runs(branch=branch)
            if runs.totalCount == 0:
                print(" Nessun run trovato ancora, aspetto...")
                time.sleep(poll_interval)
                elapsed += poll_interval
                continue
            
            latest = runs[0]

            if latest.status == "completed":
                result = latest.conclusion == "success"
                icon   = "✅" if result else "❌"
                print(f"    {icon} CI completata: {latest.conclusion}")
                return result
            else:
                print(f"   ⏳ CI in corso ({latest.status})... [{elapsed}s/{timeout_sec}s]")
                time.sleep(poll_interval)
                elapsed += poll_interval
        
        except Exception as e:
            print(f"   ⚠️  Errore polling CI: {e}")
            time.sleep(poll_interval)
            elapsed += poll_interval
        
    print(f"   ⏰ Timeout ({timeout_sec}s) — CI non completata")
    return False



def create_pull_request(repo, branch: str, base: str,
                        title: str, body: str) -> str:
    """Crea una PR e restituisce il suo URL."""
    pr = repo.create_pull(
        title=title,
        body=body,
        head=branch,
        base=base
    )

    print(f"📬 PR creata: {pr.html_url}")
    return pr.html_url