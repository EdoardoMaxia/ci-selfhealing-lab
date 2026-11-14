import random
from src.sampler import sample_value


def test_sample_distribution():
    random.seed(42)
    value = sample_value()
    random.seed(42)
    expected = random.random()
    assert value == expected