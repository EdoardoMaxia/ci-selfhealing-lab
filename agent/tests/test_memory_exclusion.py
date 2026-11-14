"""
Tests for the case_id self-retrieval exclusion in the episodic memory (Fix A3b).

The tests use a REAL ChromaDB in a temporary directory (never data/episodic_memory)
and a deterministic offline embedding function, so they need no network/API key.

Run:  python -m pytest agent/tests/test_memory_exclusion.py -v
"""
import hashlib
import re

import pytest
from chromadb import EmbeddingFunction
from chromadb.utils import embedding_functions

from agent.memory import episodic_store
from agent.memory.episodic_store import save_episode, retrieve_similar_episodes


class _HashEmbedding(EmbeddingFunction):
    """Deterministic bag-of-words hashing embedding (64 dims), offline."""

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, input):  # noqa: A002 (chromadb signature)
        out = []
        for text in input:
            v = [0.0] * 64
            for tok in re.findall(r"\w+", text.lower()):
                v[int(hashlib.md5(tok.encode()).hexdigest(), 16) % 64] += 1.0
            if not any(v):
                v[0] = 1.0
            out.append(v)
        return out

    @staticmethod
    def name():
        return "hash-embedding-test"

    def get_config(self):
        return {}

    @staticmethod
    def build_from_config(config):
        return _HashEmbedding()


@pytest.fixture(autouse=True)
def isolated_memory(tmp_path, monkeypatch):
    monkeypatch.setattr(episodic_store, "DB_PATH", str(tmp_path / "episodic_memory"))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(embedding_functions, "DefaultEmbeddingFunction", _HashEmbedding)
    yield


def _state(category, logs, fix):
    return {
        "error_category": category,
        "ci_job_name": "job",
        "ci_logs": logs,
        "git_diff": "",
        "repo_name": "test/repo",
        "attempts_history": [{"attempt": 1, "agent": category, "fix_applied": fix, "fix_diff": "-a\n+b"}],
    }


LOGS = "AssertionError: assert add(2, 3) == 99, test failed"


def _fixes(episodes):
    return {e["fix_applied"] for e in episodes}


def test_same_case_id_is_excluded():
    save_episode(_state("test", LOGS, "fix-test-001"), "success", case_id="test_001")
    res = retrieve_similar_episodes(LOGS, category="test", current_case_id="test_001")
    assert res == []


def test_other_case_id_is_returned():
    save_episode(_state("test", LOGS, "fix-test-001"), "success", case_id="test_001")
    res = retrieve_similar_episodes(LOGS, category="test", current_case_id="test_002")
    assert _fixes(res) == {"fix-test-001"}


def test_filter_is_cross_category():
    save_episode(_state("test", LOGS, "fix-test-001"), "success", case_id="test_001")
    save_episode(_state("dependency", "ERROR: numpy==99 not found", "fix-dep-005"), "success", case_id="dep_005")
    res = retrieve_similar_episodes(LOGS, category="test", current_case_id="test_002", top_k=5)
    assert _fixes(res) == {"fix-test-001"}          # dep_005 must not leak into category="test"
    res = retrieve_similar_episodes("ERROR: numpy==99 not found", category="dependency",
                                    current_case_id="test_002", top_k=5)
    assert _fixes(res) == {"fix-dep-005"}


def test_case_id_taken_from_state_when_not_passed():
    st = _state("test", LOGS, "fix-test-001")
    st["case_id"] = "test_001"
    save_episode(st, "success")
    assert retrieve_similar_episodes(LOGS, "test", current_case_id="test_001") == []
    assert _fixes(retrieve_similar_episodes(LOGS, "test", current_case_id="test_002")) == {"fix-test-001"}


def test_no_current_case_id_keeps_old_behaviour():
    save_episode(_state("test", LOGS, "fix-test-001"), "success", case_id="test_001")
    assert _fixes(retrieve_similar_episodes(LOGS, category="test")) == {"fix-test-001"}


def test_only_successful_false_also_filters_case():
    save_episode(_state("test", LOGS, "fix-esc-001"), "escalated", case_id="test_001")
    assert retrieve_similar_episodes(LOGS, "test", only_successful=False, current_case_id="test_001") == []
    assert _fixes(retrieve_similar_episodes(LOGS, "test", only_successful=False,
                                            current_case_id="test_002")) == {"fix-esc-001"}


def test_legacy_episode_without_case_id_is_not_excluded():
    """Episodes saved before the fix have no case_id: they are NOT filtered (documented limitation)."""
    col = episodic_store.get_collection()
    col.add(ids=["legacy"], documents=[LOGS],
            metadatas=[{"error_category": "test", "outcome": "success", "fix_applied": "fix-legacy",
                        "fix_diff": "", "attempt_number": "1", "repo_name": "", "timestamp": ""}])
    res = retrieve_similar_episodes(LOGS, category="test", current_case_id="test_001")
    assert _fixes(res) == {"fix-legacy"}
