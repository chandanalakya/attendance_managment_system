import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.utils.db import init_db, get_conn

import pytest
from src.utils.db import init_db, get_conn
from src.models.attendance import add_attendance, edit_attendance, delete_attendance, attempt_modify_audit_logs

SCHEMA = "src/schema.sql"

def seed(conn):
    conn.executescript('''
        INSERT INTO users (username, role) VALUES ('admin','admin');
        INSERT INTO courses (name) VALUES ('Math');
        INSERT INTO students (full_name, roll_no) VALUES ('Alice','R1');
        INSERT INTO enrollments (student_id, course_id) VALUES (1,1);
    ''')
    conn.commit()

def test_add_attendance_creates_audit_entry(tmp_path):
    init_db(SCHEMA)
    with get_conn() as conn:
        seed(conn)
        add_attendance(conn, course_id=1, student_id=1, status="PRESENT", taken_by_user_id=1, ip_address="192.168.1.2")
        logs = conn.execute("SELECT * FROM audit_logs").fetchall()
        assert len(logs) == 1
        assert logs[0]["action_type"] == "ADD"

def test_edit_attendance_adds_edit_log(tmp_path):
    init_db(SCHEMA)
    with get_conn() as conn:
        seed(conn)
        att_id = add_attendance(conn, course_id=1, student_id=1, status="PRESENT", taken_by_user_id=1, ip_address="127.0.0.1")
        edit_attendance(conn, attendance_id=att_id, new_status="ABSENT", user_id=1, ip_address="127.0.0.1")
        logs = conn.execute("SELECT * FROM audit_logs WHERE action_type='EDIT'").fetchall()
        assert len(logs) == 1
        assert "ABSENT" in logs[0]["details"]

def test_delete_attendance_creates_delete_log(tmp_path):
    init_db(SCHEMA)
    with get_conn() as conn:
        seed(conn)
        att_id = add_attendance(conn, course_id=1, student_id=1, status="PRESENT", taken_by_user_id=1, ip_address="127.0.0.1")
        delete_attendance(conn, attendance_id=att_id, user_id=1, ip_address="127.0.0.1")
        logs = conn.execute("SELECT * FROM audit_logs WHERE action_type='DELETE'").fetchall()
        assert len(logs) == 1

def test_audit_logs_are_immutable(tmp_path):
    init_db(SCHEMA)
    with get_conn() as conn:
        conn.execute("INSERT INTO users (username, role) VALUES ('admin','admin')")
        conn.execute("INSERT INTO audit_logs (action_type, attendance_id, user_id, ip_address, details) VALUES ('ADD', 1, 1, '127.0.0.1', 'demo')")
        conn.commit()
        with pytest.raises(Exception):
            conn.execute("UPDATE audit_logs SET details='tampered'")
        with pytest.raises(Exception):
            conn.execute("DELETE FROM audit_logs WHERE id=1")

