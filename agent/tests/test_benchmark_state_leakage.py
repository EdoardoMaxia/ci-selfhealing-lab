"""
Regression test for Fix A1 / A3: the state that experiments/benchmark.run_single_error
hands to the graph must (a) carry an opaque commit_sha that does not reveal the
ground-truth category and (b) carry the case_id used by the memory exclusion filter.

The graph is replaced by a fake, so no LLM, CI or network is needed.

Run:  python -m pytest agent/tests/test_benchmark_state_leakage.py -v
"""
import re
import sys
import types

import pytest

from experiments.dataset import DATASET


class _FakeApp:
    def __init__(self):
        self.state = None

    def invoke(self, state):
        self.state = state
        return {"attempts_history": [], "final_status": "fixed", "error_category": "dependency",
                "error_confidence": 0.9, "router_reasoning": ""}


@pytest.fixture
def fake_graph(monkeypatch):
    app = _FakeApp()
    mod = types.ModuleType("agent.graph")
    mod.app = app
    monkeypatch.setitem(sys.modules, "agent.graph", mod)
    return app


def _first(category):
    return next(d for d in DATASET if d["category"] == category)


@pytest.mark.parametrize("category", ["dependency", "test", "config"])
def test_state_has_opaque_sha_and_case_id(fake_graph, category):
    from experiments import benchmark
    case = _first(category)
    benchmark.run_single_error(case, dry_run=True, no_memory=True)
    st = fake_graph.state
    assert re.fullmatch(r"[0-9a-f]{40}", st["commit_sha"]), st["commit_sha"]
    assert case["id"].split("_")[0] not in st["commit_sha"][:8]   # what the Router prompt shows
    assert st["case_id"] == case["id"]
