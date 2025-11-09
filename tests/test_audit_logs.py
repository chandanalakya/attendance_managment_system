
import os, sqlite3
from src.utils.db import init_db
from src.models.attendance import add_attendance, edit_attendance, delete_attendance, attempt_modify_audit_logs
from src.models.audit_log import fetch_logs

SCHEMA = os.path.join(os.path.dirname(__file__), "..", "schema.sql")

def make_db(tmp_path):
    db_path = os.path.join(tmp_path, "test.db")
    os.environ["SAMS2_DB_PATH"] = db_path
    init_db(SCHEMA)
    return db_path

def seed(conn):
    conn.executescript(
        """
        INSERT INTO users (username, role) VALUES ('admin','admin');
        INSERT INTO courses (name) VALUES ('Math');
        INSERT INTO students (full_name, roll_no) VALUES ('Alice','R1');
        INSERT INTO enrollments (student_id, course_id) VALUES (1,1);
        """
    )
    conn.commit()

def test_add_edit_delete_logged(tmp_path):
    db_path = make_db(str(tmp_path))
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        seed(conn)
        att_id = add_attendance(conn, course_id=1, student_id=1, status='PRESENT', taken_by_user_id=1, ip_address='127.0.0.1')
        edit_attendance(conn, attendance_id=att_id, new_status='ABSENT', user_id=1, ip_address='127.0.0.1')
        delete_attendance(conn, attendance_id=att_id, user_id=1, ip_address='127.0.0.1')
        logs = fetch_logs(conn)
        actions = {r['action_type'] for r in logs}
        assert {'ADD','EDIT','DELETE'}.issubset(actions)

def test_immutable_audit_logs(tmp_path):
    db_path = make_db(str(tmp_path))
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        seed(conn)
        add_attendance(conn, course_id=1, student_id=1, status='PRESENT', taken_by_user_id=1, ip_address='127.0.0.1')
        raised = False
        try:
            attempt_modify_audit_logs(conn, operation='UPDATE', user_id=1, ip_address='127.0.0.1')
        except Exception:
            raised = True
        assert raised
