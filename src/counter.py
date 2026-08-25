class Counter:
    """Contatore condiviso incrementabile da più "worker" logici."""

    def __init__(self):
        self.value = 0

    def increment(self, amount=1):
        self.value += amount
        return self.value


def run_workers(counter, work_items):
    """Applica in sequenza una lista di incrementi al contatore condiviso."""
    for amount in work_items:
        counter.increment(amount)
    return counter.value
