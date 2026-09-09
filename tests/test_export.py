from src.exporter import write_csv

def test_write_csv(tmp_path):
    write_csv(str(tmp_path / "output.csv"), [["a", "1"]])
    write_csv(str(tmp_path / "output2.csv"), [["b", "2"]])
    assert (tmp_path / "output.csv").exists()
    assert (tmp_path / "output2.csv").exists()