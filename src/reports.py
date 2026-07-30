class Engine:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class ReportWriter:
    def __init__(self, engine):
        self.engine = engine

    def export(self):
        if self.engine.closed:
            raise Exception("Cannot operate on a closed database.")
        return "exported"
