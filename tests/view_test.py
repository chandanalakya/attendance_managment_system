# view_test.py
# Run: pytest -v

import sqlite3
import os
import pytest
import pandas as pd
from view_atte import (
    get_connection,
    get_student_by_roll,
    get_attendance_by_subject,
    generate_csv_bytes,
    generate_pdf_bytes,
)

TEST_DB = ":memory:"

@pytest.fixture
def conn():
    c = sqlite3.connect(TEST_DB)
    c.row_factory = sqlite3.Row
    # Load schema from view_stu.sql safely
    schema_path = os.path.join(os.path.dirname(__file__), "view_stu.sql")
    with open(schema_path, "r") as f:
        c.executescript(f.read())
    return c


def test_get_student_by_roll(conn, monkeypatch):
    monkeypatch.setattr("view_atte.get_connection", lambda db_path=...: conn)
    student = get_student_by_roll(conn, "21CSE001")
    assert student is not None
    assert student["name"] == "Chitra Madarakhandi"


def test_get_attendance_by_subject_empty(conn, monkeypatch):
    monkeypatch.setattr("view_atte.get_connection", lambda db_path=...: conn)
    df = get_attendance_by_subject(conn, 2, 3)
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_generate_csv_bytes():
    df = pd.DataFrame({"date": ["2025-11-01"], "subject": ["Math"], "status": ["Present"]})
    b = generate_csv_bytes(df)
    assert isinstance(b, bytes)
    assert "Math" in b.decode("utf-8")


def test_generate_pdf_bytes_header():
    df = pd.DataFrame({"date": ["2025-11-01"], "subject": ["Math"], "status": ["Present"]})
    b = generate_pdf_bytes(df, title="Test PDF")
    assert isinstance(b, (bytes, bytearray))
    assert b.startswith(b"%PDF")


def test_integration_download_bytes(conn, monkeypatch):
    monkeypatch.setattr("view_atte.get_connection", lambda db_path=...: conn)
    student = get_student_by_roll(conn, "21CSE001")
    df = get_attendance_by_subject(conn, student["id"], 1)
    csv_b = generate_csv_bytes(df)
    pdf_b = generate_pdf_bytes(df, title="Attendance")
    assert isinstance(csv_b, bytes)
    assert isinstance(pdf_b, (bytes, bytearray))
