def run_pipeline(queue, consumer):
    """Takes a message from the queue and routes it to the consumer, returning the result."""
    message = queue.pop(0)
    return consumer(message)
