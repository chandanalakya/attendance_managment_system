import pytest
import src.student_login as S
import mysql.connector

@pytest.mark.system
def test_end_to_end_student_registration_login_flow():
    """
    SYSTEM TEST: Complete Student Journey
    1. Register a student
    2. Admin approves the student manually
    3. Student logs in
    4. Student creates profile
    5. Fetch student profile and verify
    """

    # ---------- TEST DATA ----------
    email = "system_test_student@example.com"
    password = "SystemTest123!"
    full_name = "System Test Student"
    roll_no = "SYSTEM001"
    dept = "CSE"
    course = "AI"
    sem = "5"
    sec = "A"

    # ---------- CLEANUP PREVIOUS RUN ----------
    conn = S.get_db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM student_details WHERE user_id IN (SELECT id FROM users WHERE email=%s)", (email,))
    cur.execute("DELETE FROM users WHERE email=%s", (email,))
    conn.commit()

    # ---------- 1. STUDENT REGISTRATION ----------
    S.create_user(email, password)

    user = S.find_user_by_email(email)
    assert user is not None
    assert user["is_approved"] == 0          # Should not be approved yet

    # ---------- 2. ADMIN APPROVAL ----------
    cur.execute("UPDATE users SET is_approved=1 WHERE email=%s", (email,))
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
    cur.execute("DELETE FROM student_details WHERE user_id=%s", (user["id"],))
    cur.execute("DELETE FROM users WHERE email=%s", (email,))
    conn.commit()
    cur.close()
    conn.close()
