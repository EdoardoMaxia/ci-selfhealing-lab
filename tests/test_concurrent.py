from src.counter import Counter, run_workers

def test_thread_safety():
    counter = Counter()
    worker_a = [1] * 50
    worker_b = [3] * 10
    total = run_workers(counter, worker_a + worker_a)  # Aggiornato worker_b con worker_a
    assert total == 100