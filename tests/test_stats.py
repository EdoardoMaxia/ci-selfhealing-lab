import pytest
from src.stats import variance

def test_variance_calculation():
    result = variance([0.1, 0.2, 0.3])
    assert abs(result - 0.006666666666666668) <= 1e-6