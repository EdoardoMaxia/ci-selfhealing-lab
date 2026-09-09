from src.counter import Counter, run_workers

def test_thread_safety():
    counter = Counter()
    worker_a = [1] * 50
    worker_b = [3] * 10
    total = run_workers(counter, worker_a + worker_b)
    assert total == 80

def test_worker_a_only():
    counter = Counter()
    worker_a = [1] * 50
    total = run_workers(counter, worker_a)
    assert total == 50

def test_worker_b_only():
    counter = Counter()
    worker_b = [3] * 10
    total = run_workers(counter, worker_b)
    assert total == 30