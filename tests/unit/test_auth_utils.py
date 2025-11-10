import bcrypt
import pytest
from unittest.mock import MagicMock
import src.student_login as S

# --- Test password verification logic ---
def test_verify_password_correct():
    pw = "Secret123!"
    pw_hash = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    assert S.verify_password(pw, pw_hash) is True

def test_verify_password_incorrect():
    pw = "Secret123!"
    pw_hash = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    assert S.verify_password("wrongpass", pw_hash) is False

# --- Test create_user() with mocked DB ---
def test_create_user_inserts_to_db(monkeypatch):
    fake_cursor = MagicMock()
    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor

    # Replace DB connection function
    monkeypatch.setattr(S, "get_db_conn", lambda: fake_conn)
    S.create_user("test@domain.com", "Password123")

    fake_cursor.execute.assert_called_once()
    fake_conn.commit.assert_called_once()
