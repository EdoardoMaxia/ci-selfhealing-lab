from src.metrics import increment_counter, reset, make_key


def test_increment_counter():
    reset()
    key_a = make_key("service-a")
    key_b = make_key("service-b")
    for _ in range(60):
        increment_counter(key_a)
    for _ in range(40):
        increment_counter(key_b)
    assert increment_counter(key_a) == 61
    assert increment_counter(key_b) == 41
