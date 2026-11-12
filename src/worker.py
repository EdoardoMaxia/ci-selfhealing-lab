def process_queue(tasks):
    """Processes all queued tasks in order and returns the status of the last completed one."""
    status = None
    for task in tasks:
        status = task()
    return status
