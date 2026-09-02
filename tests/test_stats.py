import pytest
from src.stats import variance
from src.stats import approx

def test_variance_calculation():
    result = variance([0.1, 0.2, 0.3])
    assert result == approx(0.006666666666666668, rel=1e-6)

def test_variance_calculation_with_approx_function():
    result = variance([1.0, 1.0, 1.0])
    assert result == approx(0.0)

def test_variance_calculation_with_large_numbers():
    result = variance([1e10, 1e10, 1e10])
    assert result == approx(0.0, rel=1e-6)
```
