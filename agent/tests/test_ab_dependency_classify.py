"""classify()/build_injected() of experiments/ab_dependency_agent.py (pure functions, no LLM)."""
from experiments.ab_dependency_agent import build_injected, classify

ORIG = "pytest==7.4.0\npytest-cov==4.1.0\n"
DIFF = "+pandas==999.0.0\n"
INJ = build_injected(ORIG, DIFF)


def test_injection_matches_benchmark_logic():
    assert INJ == ORIG + "\npandas==999.0.0"


def test_valid_fix():
    assert classify(ORIG, INJ, "pytest==7.4.0\npytest-cov==4.1.0\npandas==2.0.3\n", DIFF) == []


def test_dropped_base_lines():       # Mistral's first-attempt failure on dep_002
    assert classify(ORIG, INJ, "pandas==1.4.3", DIFF) == ["dropped_base_lines"]


def test_backtick_and_dropped():     # dep_003 / dep_005
    out = "`pytest==7.4.0\nscikit-learn==1.3.2`"
    assert set(classify(ORIG, INJ, out, "+scikit-learn==0.0.1\n")) >= {"backtick", "dropped_base_lines"}


def test_unchanged_and_bad_pin_kept():
    p = classify(ORIG, INJ, INJ, DIFF)
    assert "unchanged" in p and "bad_pin_kept" in p
