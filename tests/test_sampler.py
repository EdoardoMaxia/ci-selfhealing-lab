import random
from src.sampler import sample_value

def test_sample_distribution():
    random.seed(42)
    value = sample_value()
    expected = 0.6394267984578837  # valore atteso con seed 42
    assert value == expected

def test_sample_distribution_with_different_seed():
    random.seed(100)
    value = sample_value()
    expected = 0.1456692551041303  # valore atteso con seed 100
    assert value == expected