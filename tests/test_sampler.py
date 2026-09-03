import random
from src.sampler import sample_value


def test_sample_distribution():
    # Assicuriamo che il seed sia fisso per rendere il test deterministico
    random.seed(42)
    value = sample_value()
    expected = random.random()
    assert value == expected