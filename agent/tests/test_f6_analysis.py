"""
F6 (MSR revision): correct-repair classification. Deterministic: no LLM, no network, no git.

Run:  python -m pytest agent/tests/test_f6_analysis.py -v
"""
import json
import re
from pathlib import Path

import pytest

from experiments import f6_analysis as f6
from experiments.benchmark import EXCLUDED_CASES, ORIGINAL_REQUIREMENTS, reference_state
from experiments.dataset import DATASET

REPO_ROOT = Path(__file__).resolve().parents[2]
BY_ID = {e["id"]: e for e in DATASET}
INCLUDED_DEP = sorted(e["id"] for e in DATASET if e["category"] == "dependency" and e["id"] not in EXCLUDED_CASES)
CI = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")


def clean(cid):
    return reference_state(BY_ID[cid])[1]


def test_spec_covers_every_included_dependency_case():
    assert sorted(f6.DEP_SPEC) == INCLUDED_DEP
    for cid, spec in f6.DEP_SPEC.items():
        assert set(spec) <= {"need", "alts", "removable", "marker", "options", "stable"}, cid
        for alt in spec.get("alts", []):
            assert set(alt) <= set(spec["need"]), cid


@pytest.mark.parametrize("cid,text,cls,ok", [
    # A: the injected pin is a duplicate of a package the clean file declares
    ("dep_025", ORIGINAL_REQUIREMENTS + "click==8.1.7\n", "A", True),
    # A on a package-less injection (YAML line)
    ("dep_044", ORIGINAL_REQUIREMENTS, "A", True),
    # "A" that is a removal: follows rule D
    ("dep_001", ORIGINAL_REQUIREMENTS, "D", False),
    ("dep_015", ORIGINAL_REQUIREMENTS, "D", True),
    ("dep_048", ORIGINAL_REQUIREMENTS + "boto3==1.34.10\n", "D", True),
    # B: back to the "-" line
    ("dep_002", ORIGINAL_REQUIREMENTS + "\npandas==2.0.3", "B", True),
    ("dep_009", ORIGINAL_REQUIREMENTS + "pandas==1.5.3\nscipy==1.9.0\n", "B", True),
    # C: another coherent version / alternative of expected_fix
    ("dep_002", ORIGINAL_REQUIREMENTS + "pandas==2.2.2\n", "C", True),
    ("dep_009", ORIGINAL_REQUIREMENTS + "pandas==2.0.0\nscipy==1.11.0\n", "C", True),
    ("dep_012", ORIGINAL_REQUIREMENTS + "typing-extensions>=4.6.0\nsqlalchemy==2.0.0\npydantic==2.0.0\n", "C-loose", True),
    # E: incoherent version, extra package, clean line touched, loosened below the bound
    ("dep_003", ORIGINAL_REQUIREMENTS + "scikit-learn==1.2.2\n", "E", None),
    ("dep_002", ORIGINAL_REQUIREMENTS + "pandas==2.0.3\nnumpy==1.26.4\n", "E", None),
    ("dep_002", "pytest==7.2.0\npytest-cov==4.1.0\npandas==2.0.3\n", "E", None),
    ("dep_006", ORIGINAL_REQUIREMENTS + "tensorflow>=2.0\n", "E", None),
    # normalization: order, spaces, blank lines and comments do not count
    ("dep_002", "  pandas == 2.0.3  # restored\n\npytest-cov==4.1.0\npytest==7.4.0\n", "B", True),
])
def test_classify_dependency(cid, text, cls, ok):
    got_cls, got_ok, reason = f6.classify_dependency(cid, text)
    assert (got_cls, got_ok) == (cls, ok), reason


def test_classify_config():
    assert f6.classify_config("conf_001", CI)[:2] == ("A", True)
    first = CI.replace('python-version: "3.11"', 'python-version: "3.12"', 1)
    assert f6.classify_config("conf_003", first)[:2] == ("C", True)
    assert f6.classify_config("conf_001", first)[0] == "E"                 # conf_001 admits only 3.11
    last = 'python-version: "3.12"'.join(CI.rsplit('python-version: "3.11"', 1))
    assert f6.classify_config("conf_003", last)[0] == "E"                  # another job
    assert f6.classify_config("conf_013", CI.replace("Set up Python 3.11", "Set up Python", 1))[0] == "E"


def test_ast_equal_ignores_formatting_only():
    assert f6._ast_equal("x = 1\n\n\nassert x == 1  # c\n", "x=1\nassert x==1\n")
    assert not f6._ast_equal("assert power(2, 3) == 8\n", "assert power(2, 4) == 16\n")


def test_a2_review_matches_a2_section_5_5():
    from collections import Counter
    cnt = Counter(f6.A2_REVIEW.values())
    assert cnt == {"valid": 13, "adapted": 10, "weakened": 4, "incomplete": 1}       # 28 differing fixes


def test_review_file_is_well_formed():
    data = json.loads(f6.REVIEW_FILE.read_text(encoding="utf-8"))
    allowed = {"E-extra", "E-touch", "E-incoherent", "C-loose", "D", "valid", "adapted", "weakened", "incomplete"}
    for r in data["reviews"]:
        assert r["case_id"] in BY_ID and r["case_id"] not in EXCLUDED_CASES
        assert r["class"] in allowed and isinstance(r["correct"], bool) and r["reason"]
        assert r["correct"] == (r["class"] in {"C-loose", "D", "valid"}), r
        assert r["arm"] in ("baseline", "memory")


def test_classification_file_is_consistent():
    data = json.loads(f6.CLASSIFICATION_FILE.read_text(encoding="utf-8"))
    ents = data["entries"]
    keys = [(e["arm"], e["model_id"], e["case_id"]) for e in ents]
    assert len(keys) == len(set(keys)) == 638
    assert all(isinstance(e["correct"], bool) for e in ents)
    assert all(e.get("diff") for e in ents if e["class"].startswith("E"))     # every E carries its diff
    assert all(e["source"] == "A2 §5.5" for e in ents if e["arm"] == "baseline" and e["category"] == "test")
    review = {(r["arm"], r["model_id"], r["case_id"]) for r in json.loads(f6.REVIEW_FILE.read_text())["reviews"]}
    assert review <= set(keys)
