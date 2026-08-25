def process_queue(tasks):
    """Elabora in ordine tutti i task in coda e ritorna lo stato dell'ultimo completato."""
    status = None
    for task in tasks:
        status = task()
    return status
