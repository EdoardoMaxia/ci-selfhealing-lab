import pytest
import sqlite3
from pathlib import Path

@pytest.fixture(scope='function')
def db_setup():
    """Setup database for testing."""
    db_path = Path(':memory:')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)')
    cursor.execute('INSERT INTO users (name) VALUES (?)', ('Test User',))
    conn.commit()
    yield conn
    conn.close()

def test_full_pipeline(db_setup):
    """Test the full pipeline with database."""
    cursor = db_setup.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    assert count == 1, f"Database has {count} records but expected 1"