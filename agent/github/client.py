import os
import time
import logging
from github import Github
from github.GithubException import GithubException, UnknownObjectException
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger("agent.github.client")

# Number of attempts and delay between attempts for Contents API calls
# made right after create_branch(): the new ref may not be visible yet for
# a few seconds, both for reads (repo.get_contents) and for writes
# (repo.update_file/create_file — the "create-or-update-file-contents"
# endpoint), independently of each other: it was verified that
# repo.get_contents() can succeed on the first attempt while the following
# repo.update_file() still returns 404, so both operations must be retried
# separately, not only the SHA read.
GET_CONTENTS_RETRIES = 3
GET_CONTENTS_RETRY_DELAY_SEC = 2


def get_github_client():
    """Returns an authenticated GitHub client."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not found in .env")
    return Github(token)


def get_repo(repo_name: str):
    """Returns the PyGitHub repo object"""
    g = get_github_client()
    return g.get_repo(repo_name)


def create_branch(repo, base_sha: str, branch_name: str) -> None:
    """Creates a new branch starting from the specified commit SHA."""
    try:
        repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=base_sha,
        )
        print(f"🌿 Branch created: {branch_name}")
    except Exception as e:
        if "Reference already exists" in str(e):
            print(f"🌿 Branch already exists: {branch_name}")
        else:
            raise


def _get_contents_with_retry(repo, file_path: str, branch: str):
    """
    Retrieves the content/SHA of a file on a branch, with retry+backoff.

    Right after create_branch(), the new ref may not yet be visible to the
    Contents API (repo.get_contents) even though it already exists at the
    Git Data API level — GitHub propagates the two subsystems asynchronously.
    Without retries this results in a systematic 404 on commit_file() for
    freshly created branches. Re-raises the last UnknownObjectException if
    all attempts fail, so that the caller can still distinguish
    "file not found" from other errors.
    """
    def _call():
        return repo.get_contents(file_path, ref=branch)

    return _call_with_retry(_call, op_name="get_contents", file_path=file_path, branch=branch)


def _call_with_retry(func, *, op_name: str, file_path: str, branch: str):
    """
    Runs func(), retrying up to GET_CONTENTS_RETRIES times if it raises
    UnknownObjectException (404), waiting GET_CONTENTS_RETRY_DELAY_SEC between
    attempts. Used both for reads (get_contents) and for writes
    (update_file/create_file, the "create-or-update-file-contents"
    endpoint) because both can independently return 404 right after
    create_branch(), due to the asynchronous propagation of the new ref on
    GitHub's side. Re-raises the last UnknownObjectException if all
    attempts fail.
    """
    last_exc = None
    for attempt in range(1, GET_CONTENTS_RETRIES + 1):
        log.info(
            f"{op_name}: path={file_path!r} ref={branch!r} "
            f"(attempt {attempt}/{GET_CONTENTS_RETRIES})"
        )
        try:
            return func()
        except UnknownObjectException as e:
            last_exc = e
            if attempt < GET_CONTENTS_RETRIES:
                log.warning(
                    f"{op_name}: 404 on path={file_path!r} ref={branch!r} "
                    f"(attempt {attempt}/{GET_CONTENTS_RETRIES}) — "
                    f"likely asynchronous branch propagation, "
                    f"retrying in {GET_CONTENTS_RETRY_DELAY_SEC}s"
                )
                time.sleep(GET_CONTENTS_RETRY_DELAY_SEC)
    raise last_exc


def commit_file(repo, branch: str, file_path: str,
                new_content: str, commit_message: str) -> None:
    """
    Commits a single file on an existing branch.
    Handles both new files and updates.
    """
    # Normalize the path for the GitHub Contents API, which always expects
    # forward slashes (never backslashes — relevant if file_path comes from a
    # Path built with os.sep on Windows) and no leading slash.
    normalized_path = file_path.replace("\\", "/").lstrip("/")
    if normalized_path != file_path:
        log.warning(f"commit_file: normalized path {file_path!r} -> {normalized_path!r}")
    file_path = normalized_path

    # 1. Fetch the current file to get its SHA (required for the
    #    update). A 404 here, even after the retries, means the file does
    #    not exist yet on this branch -> it must be created, not updated.
    try:
        existing = _get_contents_with_retry(repo, file_path, branch)
    except UnknownObjectException as e:
        log.warning(
            f"create_file: path={file_path!r} branch={branch!r} — "
            f"file not found after {GET_CONTENTS_RETRIES} attempts "
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
                f"create_file failed: path={file_path!r} branch={branch!r} "
                f"status={getattr(e2, 'status', '?')} data={getattr(e2, 'data', '?')}"
            )
            raise
        print(f"✍️  File created: {file_path}")
        return
    except GithubException as e:
        log.error(
            f"get_contents failed: path={file_path!r} branch={branch!r} "
            f"status={getattr(e, 'status', '?')} data={getattr(e, 'data', '?')}"
        )
        raise

    # 2. The file already exists on this branch -> update it. update_file()
    #    (same "create-or-update-file-contents" endpoint as create_file())
    #    may in turn return 404 due to asynchronous branch propagation
    #    even when the previous get_contents already succeeded —
    #    it must be retried separately.
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
            f"update_file failed: path={file_path!r} branch={branch!r} "
            f"status={getattr(e, 'status', '?')} data={getattr(e, 'data', '?')}"
        )
        raise
    print(f"✍️  File updated: {file_path}")



def wait_for_ci(repo, branch: str,
                timeout_sec: int = 300,
                poll_interval: int = 15) -> bool:
    
    """
    Waits for the CI to complete on the specified branch.
    Returns True if the CI is green, False otherwise.
    Default timeout: 5 minutes.
    """
    print(f"⏳ Waiting for the CI on branch '{branch}'...")
    elapsed = 0

    while elapsed < timeout_sec:
        try:
            runs = repo.get_workflow_runs(branch=branch)
            if runs.totalCount == 0:
                print(" No run found yet, waiting...")
                time.sleep(poll_interval)
                elapsed += poll_interval
                continue
            
            latest = runs[0]

            if latest.status == "completed":
                result = latest.conclusion == "success"
                icon   = "✅" if result else "❌"
                print(f"    {icon} CI completed: {latest.conclusion}")
                return result
            else:
                print(f"   ⏳ CI in progress ({latest.status})... [{elapsed}s/{timeout_sec}s]")
                time.sleep(poll_interval)
                elapsed += poll_interval
        
        except Exception as e:
            print(f"   ⚠️  CI polling error: {e}")
            time.sleep(poll_interval)
            elapsed += poll_interval
        
    print(f"   ⏰ Timeout ({timeout_sec}s) — CI not completed")
    return False



def create_pull_request(repo, branch: str, base: str,
                        title: str, body: str) -> str:
    """Creates a PR and returns its URL."""
    pr = repo.create_pull(
        title=title,
        body=body,
        head=branch,
        base=base
    )

    print(f"📬 PR created: {pr.html_url}")
    return pr.html_url