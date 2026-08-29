import pytest
from src.integration_db import get_connection


@pytest.fixture(scope='session')
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
    assert count == 0


def test_divisione_per_zero():
    with pytest.raises(ValueError):
        divide(1, 0)


def test_setup():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    assert len(rows) == 1
    conn.close()


def test_full_pipeline_with_setup(db_setup):
    count = db_setup.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == 1