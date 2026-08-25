def run_pipeline(queue, consumer):
    """Preleva un messaggio dalla coda e lo instrada al consumer, ritornando il risultato."""
    message = queue.pop(0)
    return consumer(message)
