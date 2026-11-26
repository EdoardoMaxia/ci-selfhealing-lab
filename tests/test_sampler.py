import random
from src.sampler import sample_value

def test_sample_distribution():
    random.seed(42)
    value = sample_value()
    expected = random.uniform(0.38, 0.46)  # update expected value range
    assert value > expected
