import pytest
from src import student_login as S
from src.utils.db import init_db, get_conn
import os

@pytest.mark.system
def test_end_to_end_student_registration_login_flow(tmp_path):
    # Temporary DB
    test_db = tmp_path / "test.db"
    os.environ["ATTENDANCE_DB"] = str(test_db)
    init_db()  # initialize schema

    email = "system_test_student@example.com"
    password = "SystemTest123!"
    full_name = "System Test Student"
    roll_no = "SYSTEM001"
    dept = "CSE"
    course = "AI"
    sem = "5"
    sec = "A"

    # ✅ Use context manager
    with get_conn() as conn:
        cur = conn.cursor()

        # Cleanup previous runs
        cur.execute("DELETE FROM student_details WHERE user_id IN (SELECT id FROM users WHERE email=?)", (email,))
        cur.execute("DELETE FROM users WHERE email=?", (email,))
        conn.commit()

        # 1️⃣ Student registration
        S.create_user(email, password)
        user = S.find_user_by_email(email)
        assert user is not None
        assert user["is_approved"] == 0

        # 2️⃣ Admin approval
        cur.execute("UPDATE users SET is_approved=1 WHERE email=?", (email,))
        conn.commit()
        user = S.find_user_by_email(email)
        assert user["is_approved"] == 1

        # 3️⃣ Student login
        assert S.verify_password(password, user["password_hash"]) is True

        # 4️⃣ Save student profile
        S.save_student_details(user["id"], full_name, roll_no, dept, course, sem, sec)

        # 5️⃣ Fetch profile
        details = S.get_student_details(user["id"])
        assert details["full_name"] == full_name
        assert details["roll_no"] == roll_no
        assert details["department"] == dept

        # Cleanup
        cur.execute("DELETE FROM student_details WHERE user_id=?", (user["id"],))
        cur.execute("DELETE FROM users WHERE email=?", (email,))
        conn.commit()
