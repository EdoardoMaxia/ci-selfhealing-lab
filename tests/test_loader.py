from pathlib import Path


def test_load_csv():
    path = '/home/dev/project/data/sample.csv'
    content = path.read_text(encoding='utf-8')
    assert 'col1' in content
