import random
from src.sampler import sample_value

def test_sample_distribution():
    random.seed(42)
    value = sample_value()
    expected = 0.6394267984578837  # Expected value when random.seed(42) is set
    assert value == expected