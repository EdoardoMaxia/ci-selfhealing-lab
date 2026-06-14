import threading
from collections import Counter

class ThreadSafeCounter:
    def __init__(self):
        self.counter = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.counter += 1

def test_thread_safety():
    """Test che verifica la thread safety del counter."""
    counter = ThreadSafeCounter()
    results = Counter()

    def increment_counter(thread_id):
        for _ in range(50):
            counter.increment()
        results[thread_id] = results.get(thread_id, 0) + 50

    thread1 = threading.Thread(target=increment_counter, args=(1,))
    thread2 = threading.Thread(target=increment_counter, args=(2,))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    assert counter.counter == 100, f"Race condition detected: counter incremented {counter.counter} times instead of 100"
    assert results == Counter({1: 50, 2: 50}), "Threading issue: lock not acquired correctly"