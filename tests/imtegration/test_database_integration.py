import pytest
import os
import mysql.connector
import src.student_login as S
from src.utils.db import SCHEMA, init_db  # assuming you have init_db function to run schema.sql

@pytest.mark.integration
def test_user_insert_and_fetch():
    """Integration test: create and fetch a student user"""

    # ---------- TEST DATA ----------
    email = "integration_test@example.com"
    password = "Integration@123"

    # ---------- INIT DB ----------
    init_db(SCHEMA)  # Ensure tables exist

    # ---------- CONNECT ----------
    conn = S.get_db_conn()
    assert conn is not None, "Database connection failed"
    cur = conn.cursor(dictionary=True)

    # ---------- CLEANUP PREVIOUS RECORD ----------
    cur.execute("DELETE FROM users WHERE email=%s", (email,))
    conn.commit()

    # ---------- CREATE USER ----------
    S.create_user(email, password)

    # ---------- FETCH USER ----------
    user = S.find_user_by_email(email)
    assert user is not None
    assert user["email"] == email

    # ---------- CLEANUP ----------
    cur.execute("DELETE FROM users WHERE email=%s", (email,))
    conn.commit()
    cur.close()
    conn.close()
