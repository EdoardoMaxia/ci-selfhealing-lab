import pytest

def test_sum_floats():
    result = 0.1 + 0.2
    assert result == pytest.approx(0.3)