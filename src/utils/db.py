
import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.getenv("SAMS2_DB_PATH", os.path.join(os.path.dirname(__file__), "..", "sams2.db"))

def init_db(schema_path: str):
    with sqlite3.connect(DB_PATH) as conn, open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
        conn.commit()

@contextmanager
def get_conn(db_path: str = None):
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
