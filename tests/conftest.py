import sys
import os
import pytest
from src.app import init_db, get_conn, create_user

# --------------------------
# Make src importable in tests
# --------------------------
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# --------------------------
# Fixtures
# --------------------------
@pytest.fixture(autouse=True)
def fresh_db(tmp_path):
    """Provide a fresh database for every test."""
    test_db = tmp_path / "test.db"
    os.environ["ATTENDANCE_DB"] = str(test_db)
    init_db()
    yield

@pytest.fixture
def seed_basic():
    """Seed a basic set of users, course, enrollment, and attendance for tests."""
    student_id = create_user("Stu", "stu@example.com", "pass", "student")
    faculty_id = create_user("Fac", "fac@example.com", "pass", "faculty")
    admin_id   = create_user("Adm", "adm@example.com", "pass", "admin")

    with get_conn() as conn:
        # Insert course only if not exists
        row = conn.execute("SELECT id FROM courses WHERE code='CS101'").fetchone()
        if row:
            course_id = row["id"]
        else:
            conn.execute("INSERT INTO courses(code,name) VALUES(?,?)", ("CS101", "Intro CS"))
            course_id = conn.execute("SELECT id FROM courses WHERE code='CS101'").fetchone()["id"]

        # Insert enrollment only if not exists
        row = conn.execute(
            "SELECT 1 FROM enrollments WHERE student_id=? AND course_id=?",
            (student_id, course_id)
        ).fetchone()
        if not row:
            conn.execute(
                "INSERT INTO enrollments(student_id,course_id) VALUES(?,?)",
                (student_id, course_id)
            )

        # Insert initial attendance record only if not exists
        row = conn.execute(
            "SELECT 1 FROM attendance WHERE student_id=? AND course_id=? AND session_dt=?",
            (student_id, course_id, "2025-11-07T09:00:00+00:00")
        ).fetchone()
        if not row:
            conn.execute(
                "INSERT INTO attendance(student_id,course_id,session_dt,status) VALUES(?,?,?,?)",
                (student_id, course_id, "2025-11-07T09:00:00+00:00", "absent")
            )

        # Clear old correction requests to start fresh
        conn.execute("DELETE FROM attendance_corrections")

    return {
        "student_id": student_id,
        "faculty_id": faculty_id,
        "admin_id": admin_id,
        "course_id": course_id,
    }
