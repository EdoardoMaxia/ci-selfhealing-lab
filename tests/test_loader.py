from pathlib import Path
import pytest

@pytest.fixture
def sample_csv_path(tmp_path):
    # Create a temporary CSV file for testing
    csv_content = "col1,col2\nvalue1,value2"
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(csv_content, encoding='utf-8')
    return csv_file

def test_load_csv(sample_csv_path):
    path = sample_csv_path
    content = path.read_text(encoding='utf-8')
    assert 'col1' in content