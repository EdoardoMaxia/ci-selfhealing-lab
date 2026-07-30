import sqlite3


def get_connection(db_path=":memory:"):
    """Apre una connessione sqlite con la tabella 'users' pronta (per test_017)."""
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
    conn.commit()
    return conn
