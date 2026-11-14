class Counter:
    """Shared counter that can be incremented by multiple logical "workers"."""

    def __init__(self):
        self.value = 0

    def increment(self, amount=1):
        self.value += amount
        return self.value


def run_workers(counter, work_items):
    """Sequentially applies a list of increments to the shared counter."""
    for amount in work_items:
        counter.increment(amount)
    return counter.value
