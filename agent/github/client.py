import os
import time
import base64
import hashlib
import logging
from github import Github, InputGitTreeElement
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



# ══════════════════════════════════════════════════════════════
# PROTOCOL B helpers (used only by `benchmark.py --test-protocol-b` /
# `--verify-excluded` and by the Fix Executor when state["fix_base_sha"] is set).
# The functions above are unchanged and still drive the default protocol.
# ══════════════════════════════════════════════════════════════

def git_blob_sha(data: bytes) -> str:
    """SHA-1 that git assigns to a blob with this content (same as `git hash-object`)."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def commit_files_on_new_branch(repo, base_sha: str, branch: str,
                               changes: dict, commit_message: str) -> str:
    """
    Creates ONE commit on top of `base_sha` with every change in `changes`
    ({repo-relative path: bytes content, or None to delete the file}) and a new
    branch `branch` pointing at it. Returns the SHA of the new commit.

    Git Data API (blob -> tree -> commit -> ref) instead of create_branch() +
    commit_file(): the ref is created directly on the new commit, so the push
    triggers exactly one workflow run, for that commit. create_branch() on an
    existing commit triggers an extra run on the base commit (visible in the
    Actions history as a second "push" run per fix/ai-* branch).
    Contents are uploaded as base64, byte for byte.
    """
    base_commit = repo.get_git_commit(base_sha)
    base_tree   = repo.get_git_tree(base_commit.tree.sha, recursive=True)
    modes       = {e.path: e.mode for e in base_tree.tree if e.type == "blob"}

    elements = []
    for path, content in sorted(changes.items()):
        path = path.replace("\\", "/").lstrip("/")
        if content is None:
            if path in modes:   # deleting a path the base tree does not have is a no-op
                elements.append(InputGitTreeElement(path, modes[path], "blob", sha=None))
            continue
        blob = repo.create_git_blob(base64.b64encode(content).decode("ascii"), "base64")
        elements.append(InputGitTreeElement(path, modes.get(path, "100644"), "blob", sha=blob.sha))

    tree   = repo.create_git_tree(elements, base_tree=base_commit.tree) if elements else base_commit.tree
    commit = repo.create_git_commit(commit_message, tree, [base_commit])
    repo.create_git_ref(ref=f"refs/heads/{branch}", sha=commit.sha)
    print(f"🌿 Branch created: {branch} @ {commit.sha[:8]} ({len(elements)} file change(s) on {base_sha[:8]})")
    return commit.sha


def wait_for_ci_run(repo, branch: str, head_sha: str,
                    timeout_sec: int = 300, poll_interval: int = 15) -> dict:
    """
    Like wait_for_ci(), but only the "push" workflow run of `head_sha` counts:
    a run of another commit on the same branch (e.g. the one triggered by the
    branch creation) is never taken for the result. Returns
        {"conclusion": "success"|"failure"|...|None, "status": str|None,
         "run_id": int|None, "run_url": str|None, "head_sha": head_sha}
    conclusion is None when no matching run completed within timeout_sec.
    """
    print(f"⏳ Waiting for the CI run of {head_sha[:8]} on branch '{branch}'...")
    elapsed = 0
    latest  = None
    while elapsed < timeout_sec:
        try:
            runs = [r for r in repo.get_workflow_runs(branch=branch, head_sha=head_sha, event="push")
                    if r.head_sha == head_sha]
            if runs:
                latest = max(runs, key=lambda r: r.id)
                if latest.status == "completed":
                    print(f"    CI run {latest.id} completed: {latest.conclusion}")
                    return {"conclusion": latest.conclusion, "status": latest.status,
                            "run_id": latest.id, "run_url": latest.html_url, "head_sha": head_sha}
                print(f"   ⏳ CI run {latest.id} {latest.status}... [{elapsed}s/{timeout_sec}s]")
            else:
                print("    No run for this commit yet, waiting...")
        except Exception as e:
            print(f"   ⚠️  CI polling error: {e}")
        time.sleep(poll_interval)
        elapsed += poll_interval

    print(f"   ⏰ Timeout ({timeout_sec}s) — CI run of {head_sha[:8]} not completed")
    return {"conclusion": None, "status": getattr(latest, "status", None),
            "run_id": getattr(latest, "id", None), "run_url": getattr(latest, "html_url", None),
            "head_sha": head_sha}


def delete_branch(repo, branch: str) -> bool:
    """Deletes a remote branch; returns False (never raises) if it cannot."""
    try:
        repo.get_git_ref(f"heads/{branch}").delete()
        return True
    except Exception as e:
        log.warning(f"delete_branch: unable to remove {branch}: {e}")
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