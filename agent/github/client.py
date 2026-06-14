import os
import time
from github import Github
from dotenv import load_dotenv

load_dotenv()



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


def commit_file(repo, branch: str, file_path: str,
                new_content: str, commit_message: str) -> None:
    """
    Commit di un singolo file su un branch esistente.
    Gestisce sia file nuovi che aggiornamenti.
    """
    try:
        # Recupera il file attuale per ottenere il suo SHA (necessario per update)
        existing = repo.get_contents(file_path, ref=branch)
        repo.update_file(
            path=file_path,
            message=commit_message,
            content=new_content,
            sha=existing.sha,
            branch=branch
        )
        print(f"✍️  File aggiornato: {file_path}")
    except Exception as e:
        if "404" in str(e):
            # File non esiste ancora -> lo crea
            repo.create_file(
                path=file_path,
                message=commit_message,
                content=new_content,
                branch=branch
            )
            print(f"✍️  File creato: {file_path}")
        else:
            raise



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