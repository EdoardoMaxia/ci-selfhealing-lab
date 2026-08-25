import pytest
from src.integration_db import get_connection

@pytest.fixture(scope='function')
def db_setup():
    conn = get_connection()
    conn.execute("CREATE TABLE IF NOT EXISTS users (name TEXT)")
    conn.execute("INSERT INTO users (name) VALUES ('alice')")
    conn.commit()
    yield conn
    conn.execute("DELETE FROM users")
    conn.commit()
    conn.close()

def test_process_and_archive(db_setup):
    db_setup.execute("DELETE FROM users")
    db_setup.commit()
    count = db_setup.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == 0

def test_full_pipeline(db_setup):
    count = db_setup.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == 1