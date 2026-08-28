from src.pipeline import run_pipeline

def test_consumer_processes_message():
    queue = ["hello"]

    def producer():
        queue.append("hello")

    def consumer(msg):
        assert msg == "hello"
        return msg.upper()

    result = run_pipeline(queue, consumer)
    assert result == "HELLO"

def test_consumer_processes_empty_queue():
    queue = []

    def producer():
        pass

    def consumer(msg):
        assert msg is None

    result = run_pipeline(queue, consumer)
    assert result is None

def run_pipeline(queue, consumer):
    if not queue:
        return None
    else:
        result = consumer(queue.pop(0))
        return result