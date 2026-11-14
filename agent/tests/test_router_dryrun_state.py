"""
build_state() of experiments/router_dryrun.py: opaque_id / no_jobname must never show the
category prefix in the 8 chars the Router prompt displays; legacy_id (control) must
reproduce the pre-fix format exactly, so that legacy_id vs opaque_id isolates the leak.

No LLM or network needed (benchmark.py's heavy graph import is faked).

Run:  python -m pytest agent/tests/test_router_dryrun_state.py -v
"""
import sys
import types

import pytest

from experiments.dataset import DATASET


@pytest.fixture
def rd(monkeypatch):
    mod = types.ModuleType("agent.graph")
    mod.app = object()
    monkeypatch.setitem(sys.modules, "agent.graph", mod)
    from experiments import router_dryrun
    return router_dryrun


@pytest.mark.parametrize("category", ["dependency", "test", "config"])
def test_conditions(rd, category):
    case = next(d for d in DATASET if d["category"] == category)
    prefix = case["id"].split("_")[0]

    opaque = rd.build_state(case, "opaque_id")
    assert prefix not in opaque["commit_sha"][:8] and len(opaque["commit_sha"]) == 40
    assert opaque["ci_job_name"] == case["ci_job_name"]

    nojob = rd.build_state(case, "no_jobname")
    assert nojob["ci_job_name"] == "" and nojob["commit_sha"] == opaque["commit_sha"]

    legacy = rd.build_state(case, "legacy_id")
    assert legacy["commit_sha"] == f"{case['id']}_benchmark"
    assert legacy["commit_sha"][:8].startswith(prefix[:4])        # the leak the control reproduces
    assert legacy["ci_job_name"] == case["ci_job_name"]
    for k in ("ci_logs", "ci_conclusion", "git_diff"):            # everything else identical
        assert legacy[k] == opaque[k]


def test_legacy_not_in_default_both(rd):
    assert "legacy_id" not in rd.CONDITIONS and "legacy_id" in rd.CONTROL_CONDITIONS
