import pytest
from src import student_login as S
from src.utils.db import get_conn

@pytest.mark.integration
def test_user_insert_and_fetch():
    email = "integration_test@example.com"
    password = "Integration@123"

    # ✅ Use context manager for connection
    with S.get_db_conn() as conn:
        cur = conn.cursor()

        # Cleanup any previous record
        cur.execute("DELETE FROM users WHERE email=%s", (email,))
        conn.commit()

        # Insert user
        S.create_user(email, password)

        # Fetch user
        user = S.find_user_by_email(email)
        assert user is not None
        assert user["email"] == email

        # Cleanup
        cur.execute("DELETE FROM users WHERE email=%s", (email,))
        conn.commit()
