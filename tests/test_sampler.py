import random
from src.sampler import sample_value


def test_sample_distribution():
    random.seed(42)
    value = sample_value()
    assert 0 <= value <= 1


def test_sample_value_type():
    random.seed(42)
    value = sample_value()
    assert isinstance(value, float)


def test_sample_multiple_values():
    random.seed(42)
    values = [sample_value() for _ in range(10)]
    assert len(values) == 10
    assert all(0 <= v <= 1 for v in values)


def test_sample_distribution_range():
    random.seed(123)
    values = [sample_value() for _ in range(100)]
    assert all(0 <= v <= 1 for v in values)
    assert min(values) >= 0
    assert max(values) <= 1