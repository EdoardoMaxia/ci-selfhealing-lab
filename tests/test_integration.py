import pytest
from src.integration_db import get_connection


@pytest.fixture(scope='function')
def db_setup():
    conn = get_connection()
    conn.execute("INSERT INTO users (name) VALUES ('alice')")
    conn.commit()
    yield conn
    conn.close()


def test_process_and_archive(db_setup):
    db_setup.execute("DELETE FROM users")
    db_setup.commit()


def test_full_pipeline(db_setup):
    count = db_setup.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == 1
