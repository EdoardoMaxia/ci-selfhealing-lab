from src.pipeline import run_pipeline

def test_consumer_processes_message():
    queue = []
    queue.append("hello")

    def producer():
        queue.append("hello")

    def consumer(msg):
        return msg.upper()

    result = run_pipeline(queue, consumer)
    assert result == "HELLO"