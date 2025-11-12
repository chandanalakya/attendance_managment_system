import os
import sqlite3
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session

try:
    import sqlparse
except ImportError:
    sqlparse = None


# -------------------------------------------------------------------
# ✅ DATABASE CONNECTION SETUP
# -------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
DB_PATH = DATABASE_URL.replace("sqlite:///", "")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def get_db():
    """Provide a transactional session scope for ORM operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_conn(raw=False):
    """
    Provide a context-managed DB connection.

    If raw=True → returns a raw sqlite3 connection (supports executescript)
    Else → returns SQLAlchemy connection.
    """
    if raw or "sqlite" in DATABASE_URL:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
    else:
        conn = engine.connect()

    try:
        yield conn
    finally:
        conn.close()


# -------------------------------------------------------------------
# ✅ FALLBACK SCHEMA (for init_db if file not found)
# -------------------------------------------------------------------
SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    roll_no TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PRESENT','ABSENT','LATE','EXCUSED')),
    taken_at DATETIME NOT NULL DEFAULT (datetime('now')),
    taken_by_user_id INTEGER NOT NULL,
    notes TEXT,
    FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(taken_by_user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL CHECK (action_type IN ('ADD','EDIT','DELETE','LOG_MOD_ATTEMPT')),
    attendance_id INTEGER,
    user_id INTEGER NOT NULL,
    ip_address TEXT,
    details TEXT,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(attendance_id) REFERENCES attendance(id) ON DELETE SET NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS audit_security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    user_id INTEGER,
    ip_address TEXT,
    target_table TEXT,
    operation TEXT,
    details TEXT,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TRIGGER IF NOT EXISTS trg_audit_logs_prevent_update
BEFORE UPDATE ON audit_logs
BEGIN
    SELECT RAISE(ABORT, 'audit_logs are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_audit_logs_prevent_delete
BEFORE DELETE ON audit_logs
BEGIN
    SELECT RAISE(ABORT, 'audit_logs are immutable');
END;
"""
import time

import time
import gc
import sqlite3

def init_db(schema=SCHEMA):
    """
    Initialize the database.
    - Reads from inline SQL or src/schema.sql file.
    - Fully resets DB file safely (Windows lock–proof).
    """
    if os.path.exists(schema):
        with open(schema, "r", encoding="utf-8") as f:
            schema_sql = f.read()
    elif os.path.exists("src/schema.sql"):
        with open("src/schema.sql", "r", encoding="utf-8") as f:
            schema_sql = f.read()
    else:
        schema_sql = schema

    # ✅ Fully dispose of SQLAlchemy engine + garbage collect to close file handles
    try:
        engine.dispose()
        gc.collect()
        time.sleep(0.2)
        if os.path.exists(DB_PATH):
            for _ in range(5):
                try:
                    os.remove(DB_PATH)
                    break
                except PermissionError:
                    time.sleep(0.3)
    except Exception as e:
        print(f"⚠️ Cleanup failed: {e}")

    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema_sql)
        conn.commit()

    print(f"✅ Database initialized successfully from {schema if os.path.exists(schema) else 'inline SCHEMA'}")
