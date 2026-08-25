import pytest
from src.stats import variance


def test_variance_calculation():
    result = variance([0.1, 0.2, 0.3])
    assert result == pytest.approx(0.006666666666666667)
