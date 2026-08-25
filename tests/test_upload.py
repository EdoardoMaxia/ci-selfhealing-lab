from src.upload import UploadClient


def test_multipart_upload():
    client_a = UploadClient()
    client_b = UploadClient()
    client_a.upload("part1.bin")
    client_b.upload("part2.bin")
    assert client_a.uploaded == ["part1.bin"]
    assert client_b.uploaded == ["part2.bin"]
