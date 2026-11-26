def make_task(result):
    def _task():
        return result
    return _task


def test_background_task():
    tasks = [make_task("pending"), make_task("done")]
    result = process_queue(tasks)
    assert result == "pending"


def process_queue(tasks):
    for task in tasks:
        result = task()
        if result == "pending":
            return "pending"
        elif result == "done":
            return "done"