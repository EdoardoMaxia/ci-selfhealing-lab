"""
Protocol B for the "test" category (MSR 2027 revision, reviewer concern 2 / Q3).

Helpers with no LLM and no GitHub writes, used by experiments/benchmark.py when
--test-protocol-b or --verify-excluded is given:

- which files make up the failed state that the CI must see
  (local working tree vs the remote base tree, restricted to CI_SCOPE);
- mapping of a GitHub Actions conclusion to red / green / error;
- the repaired test run on the clean source (HEAD, no injected error);
- the comparison of the assertions of the original vs the repaired test.
"""
import ast
import os
import io
import sys
import json
import shutil
import tarfile
import tempfile
import subprocess
from pathlib import Path

from agent.github.client import git_blob_sha

# Everything the CI job reads: `pip install -r requirements.txt` and
# `pytest tests/ --cov=src` (PYTHONPATH = repo root, app/ imported by tests).
CI_SCOPE = ("src", "app", "tests", "requirements.txt", ".github/workflows")

# Root-level files that would change how pytest runs, copied too if tracked.
PYTEST_ROOT_FILES = ("conftest.py", "pytest.ini", "setup.cfg", "tox.ini", "pyproject.toml")


def in_scope(path: str) -> bool:
    path = path.replace("\\", "/")
    return any(path == s or path.startswith(s + "/") for s in CI_SCOPE)


# ──────────────────────────────────────────────────────────────
# Failed state = local working tree vs remote base tree
# ──────────────────────────────────────────────────────────────

def local_scope_files(repo_root: Path = Path(".")) -> set:
    """Tracked + untracked-not-ignored files under CI_SCOPE that exist on disk."""
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", *CI_SCOPE],
        cwd=repo_root, capture_output=True, text=True, check=True,
    ).stdout
    return {p for p in out.splitlines() if p and (repo_root / p).is_file()}


def remote_scope_blobs(repo, base_sha: str) -> dict:
    """{path: blob sha} of the files under CI_SCOPE in the tree of commit base_sha."""
    commit = repo.get_git_commit(base_sha)
    tree = repo.get_git_tree(commit.tree.sha, recursive=True)
    if getattr(tree, "raw_data", {}).get("truncated"):
        raise RuntimeError(f"tree of {base_sha[:8]} is truncated by the GitHub API")
    return {e.path: e.sha for e in tree.tree if e.type == "blob" and in_scope(e.path)}


def diff_against_remote(remote_blobs: dict, repo_root: Path = Path(".")) -> dict:
    """
    Changes that turn the remote base tree into the local working tree (CI_SCOPE only):
    {path: bytes} for added/modified files, {path: None} for deleted ones.
    """
    changes = {}
    local = local_scope_files(repo_root)
    for path in sorted(local | set(remote_blobs)):
        if path in local:
            data = (repo_root / path).read_bytes()
            if remote_blobs.get(path) != git_blob_sha(data):
                changes[path] = data
        elif path in remote_blobs:
            changes[path] = None
    return changes


def ci_status(conclusion) -> str:
    """GitHub Actions conclusion -> red / green / error (timeout, cancelled, ...)."""
    if conclusion == "success":
        return "green"
    if conclusion == "failure":
        return "red"
    return "error"


# ──────────────────────────────────────────────────────────────
# Repaired test on the clean source
# ──────────────────────────────────────────────────────────────

def _extract_clean_tree(dest: Path, repo_root: Path, ref: str) -> None:
    tracked = subprocess.run(["git", "ls-files", "--", *PYTEST_ROOT_FILES],
                             cwd=repo_root, capture_output=True, text=True).stdout.split()
    paths = [p for p in ("src", "app", "tests", "requirements.txt") if subprocess.run(
        ["git", "cat-file", "-e", f"{ref}:{p}"], cwd=repo_root, capture_output=True).returncode == 0]
    archive = subprocess.run(["git", "archive", "--format=tar", ref, "--", *paths, *tracked],
                             cwd=repo_root, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        try:
            tar.extractall(dest, filter="data")
        except TypeError:          # Python without tarfile extraction filters
            tar.extractall(dest)


def run_test_on_clean_source(test_rel_path: str, repaired: bytes,
                             repo_root: Path = Path("."), ref: str = "HEAD",
                             timeout: int = 120) -> dict:
    """
    Runs `pytest <test_rel_path>` on a fresh copy of `ref` (the clean source, i.e.
    WITHOUT the injected error) in which only the test file is replaced by the
    repaired one. Fresh directory + -B: no stale bytecode can leak in.
    result: pass | fail (tests failed or not collectable) | no_tests | error.
    """
    tmp = Path(tempfile.mkdtemp(prefix="a2-clean-"))
    try:
        _extract_clean_tree(tmp, repo_root, ref)
        target = tmp / test_rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(repaired)
        env = {**os.environ, "PYTHONPATH": str(tmp), "PYTHONDONTWRITEBYTECODE": "1"}
        proc = subprocess.run(
            [sys.executable, "-B", "-m", "pytest", test_rel_path, "-q",
             "-p", "no:cacheprovider", "-o", "addopts="],
            cwd=tmp, env=env, capture_output=True, text=True, timeout=timeout,
        )
        last = (proc.stdout.strip().splitlines() or [""])[-1][:200]
        result = {0: "pass", 1: "fail", 2: "fail", 5: "no_tests"}.get(proc.returncode, "error")
        return {"result": result, "returncode": proc.returncode, "summary": last}
    except subprocess.TimeoutExpired:
        return {"result": "error", "returncode": None, "summary": f"timeout after {timeout}s"}
    except Exception as e:
        return {"result": "error", "returncode": None, "summary": f"{type(e).__name__}: {e}"[:200]}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ──────────────────────────────────────────────────────────────
# Assertions: original vs repaired
# ──────────────────────────────────────────────────────────────

# pytest helpers that assert by themselves (pytest.raises / raises / ...).
_PYTEST_ASSERT_HELPERS = {"raises", "warns", "fail", "deprecated_call"}


def _is_assert_call(node) -> bool:
    if not isinstance(node, ast.Call):
        return False
    f = node.func
    if isinstance(f, ast.Attribute):
        if f.attr.startswith("assert"):            # self.assertEqual, mock.assert_called_once_with, ...
            return True
        return (f.attr in _PYTEST_ASSERT_HELPERS
                and isinstance(f.value, ast.Name) and f.value.id == "pytest")
    if isinstance(f, ast.Name):
        return f.id in _PYTEST_ASSERT_HELPERS or f.id.startswith("assert")
    return False


def _text(node) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return ast.dump(node)


def extract_assertions(source: str) -> list:
    """
    Every assertion of a test module, with the test function/class it belongs to:
    `assert` statements, assert*() calls and pytest.raises/warns/fail/deprecated_call.
    The text is ast.unparse()d, so formatting differences do not count as changes.
    """
    tree = ast.parse(source)
    found = []

    def visit(node, scope):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                visit(child, f"{scope}.{child.name}" if scope else child.name)
            elif isinstance(child, ast.Assert) or _is_assert_call(child):
                found.append({"scope": scope or "<module>", "text": _text(child), "line": child.lineno})
            else:
                visit(child, scope)

    visit(tree, "")
    return found


def compare_assertions(original: str, repaired: str) -> dict:
    """
    Matches the assertions of `original` against `repaired`:
      kept     — same text, same test (or same text in a renamed/moved test: "moved_to")
      modified — no textual match, but the same test has an unmatched assertion (paired in order)
      removed  — no counterpart in the repaired file
      added    — assertions of the repaired file left unmatched
    summary = "kept/modified/removed" ("parse_error" if a file does not parse).
    """
    try:
        orig = extract_assertions(original)
    except SyntaxError as e:
        return {"summary": "parse_error", "error": f"original: {e}"}
    try:
        rep = extract_assertions(repaired)
    except SyntaxError as e:
        return {"summary": "parse_error", "error": f"repaired: {e}"}

    pool = list(rep)

    def take(pred):
        for b in pool:
            if pred(b):
                pool.remove(b)
                return b
        return None

    kept, rest = [], []
    for a in orig:
        if take(lambda b: b["scope"] == a["scope"] and b["text"] == a["text"]):
            kept.append({"scope": a["scope"], "text": a["text"]})
        else:
            rest.append(a)
    modified, removed, rest2 = [], [], []
    for a in rest:
        b = take(lambda b: b["text"] == a["text"])
        if b:
            kept.append({"scope": a["scope"], "text": a["text"], "moved_to": b["scope"]})
        else:
            rest2.append(a)
    for a in rest2:
        b = take(lambda b: b["scope"] == a["scope"])
        if b:
            modified.append({"scope": a["scope"], "original": a["text"], "repaired": b["text"]})
        else:
            removed.append({"scope": a["scope"], "text": a["text"]})
    added = [{"scope": b["scope"], "text": b["text"]} for b in pool]

    return {
        "summary":  f"{len(kept)}/{len(modified)}/{len(removed)}",
        "counts":   {"original": len(orig), "repaired": len(rep), "kept": len(kept),
                     "modified": len(modified), "removed": len(removed), "added": len(added)},
        "kept":     kept,
        "modified": modified,
        "removed":  removed,
        "added":    added,
    }


def assertions_report(baseline: str, injected: str, repaired: str) -> tuple:
    """
    (assertions_preserved, assertions_detail JSON). The reference for
    "preserved" is the ORIGINAL test, i.e. the clean baseline before the
    injection; the comparison with the injected (broken) version is kept in
    the detail, because the injection itself may change an assertion.
    """
    vs_base = compare_assertions(baseline, repaired)
    vs_inj  = compare_assertions(injected, repaired) if injected is not None else None
    detail = {"reference": "baseline (clean test before injection)",
              "vs_baseline": vs_base, "vs_injected": vs_inj}
    return vs_base["summary"], json.dumps(detail, ensure_ascii=False)
