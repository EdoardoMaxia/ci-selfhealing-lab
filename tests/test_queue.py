from src.pipeline import run_pipeline

def test_consumer_processes_message():
    queue = []

    def producer():
        queue.append("hello")

    def consumer(msg):
        return msg.upper()

    producer()
    result = run_pipeline(queue, consumer)  # <--- FIX MINIMALE: restituisci la coda popolata
    assert result == "HELLO"