class UploadClient:
    def __init__(self):
        self.uploaded = []

    def upload(self, filename):
        self.uploaded.append(filename)
        return len(self.uploaded)
