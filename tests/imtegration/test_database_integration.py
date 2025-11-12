import pytest
import os
from src.utils.db import init_db, get_conn
from src import student_login as S  # adjust if your module name is different

@pytest.mark.integration
def test_user_insert_and_fetch(tmp_path):
    # -------------------------------
    # Create a fresh temporary database
    # -------------------------------
    test_db = tmp_path / "test.db"
    os.environ["ATTENDANCE_DB"] = str(test_db)

    # Initialize DB schema
    init_db()

    email = "integration_test@example.com"
    password = "Integration@123"

    # -------------------------------
    # Connect to DB
    # -------------------------------
    conn = get_conn()
    assert conn is not None, "Failed to get database connection"
    cur = conn.cursor()

    # -------------------------------
    # Cleanup any previous record
    # -------------------------------
    cur.execute("DELETE FROM users WHERE email=?", (email,))
    conn.commit()

    # -------------------------------
    # Insert user
    # -------------------------------
    S.create_user(email, password)

    # -------------------------------
    # Fetch user and validate
    # -------------------------------
    user = S.find_user_by_email(email)
    assert user is not None, "User not found in database"
    assert user["email"] == email

    # -------------------------------
    # Cleanup after test
    # -------------------------------
    cur.execute("DELETE FROM users WHERE email=?", (email,))
    conn.commit()
    cur.close()
    conn.close()
