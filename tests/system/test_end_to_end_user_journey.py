import pytest
import os
from src import student_login as S
from src.utils.db import init_db, get_conn

@pytest.mark.system
def test_end_to_end_student_registration_login_flow(tmp_path):
    """
    SYSTEM TEST: Complete Student Journey
    1. Register a student
    2. Admin approves the student manually
    3. Student logs in
    4. Student creates profile
    5. Fetch student profile and verify
    """

    # -----------------------------
    # Create a temporary database
    # -----------------------------
    test_db = tmp_path / "test.db"
    os.environ["ATTENDANCE_DB"] = str(test_db)
    init_db()  # Initialize schema

    # ---------- TEST DATA ----------
    email = "system_test_student@example.com"
    password = "SystemTest123!"
    full_name = "System Test Student"
    roll_no = "SYSTEM001"
    dept = "CSE"
    course = "AI"
    sem = "5"
    sec = "A"

    # ---------- CONNECT ----------
    conn = get_conn()
    assert conn is not None, "Failed to get database connection"
    cur = conn.cursor()

    # ---------- CLEANUP PREVIOUS RUN ----------
    cur.execute(
        "DELETE FROM student_details WHERE user_id IN (SELECT id FROM users WHERE email=?)",
        (email,)
    )
    cur.execute("DELETE FROM users WHERE email=?", (email,))
    conn.commit()

    # ---------- 1. STUDENT REGISTRATION ----------
    S.create_user(email, password)
    user = S.find_user_by_email(email)
    assert user is not None
    assert user["is_approved"] == 0

    # ---------- 2. ADMIN APPROVAL ----------
    cur.execute("UPDATE users SET is_approved=1 WHERE email=?", (email,))
    conn.commit()
    user = S.find_user_by_email(email)
    assert user["is_approved"] == 1

    # ---------- 3. STUDENT LOGIN ----------
    assert S.verify_password(password, user["password_hash"]) is True

    # ---------- 4. STUDENT PROFILE SAVE ----------
    S.save_student_details(
        user["id"], full_name, roll_no, dept, course, sem, sec
    )

    # ---------- 5. FETCH PROFILE ----------
    details = S.get_student_details(user["id"])
    assert details is not None
    assert details["full_name"] == full_name
    assert details["roll_no"] == roll_no
    assert details["department"] == dept

    # ---------- CLEANUP ----------
    cur.execute("DELETE FROM student_details WHERE user_id=?", (user["id"],))
    cur.execute("DELETE FROM users WHERE email=?", (email,))
    conn.commit()
    cur.close()
    conn.close()
