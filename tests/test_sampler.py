import random
from src.sampler import sample_value


def test_sample_distribution():
    random.seed(42)
    value = sample_value()
    random.seed(42)
    expected = random.random()
    assert value == expected


def test_sample_value_returns_float():
    random.seed(42)
    value = sample_value()
    assert isinstance(value, float)


def test_sample_value_in_range():
    random.seed(42)
    value = sample_value()
    assert 0 <= value <= 1


def test_sample_value_deterministic():
    random.seed(123)
    value1 = sample_value()
    random.seed(123)
    value2 = sample_value()
    assert value1 == value2