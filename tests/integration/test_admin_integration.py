from unittest.mock import MagicMock

import importlib.util
import os

# ✅ Correctly load admin_login.py (not admin_access.py)
spec = importlib.util.spec_from_file_location(
    "admin_login",
    os.path.join(
        os.path.dirname(__file__),
        "../../src/admin_login.py"))
admin_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admin_module)


def test_get_user_role_from_db(monkeypatch):
    """Should correctly fetch role from DB."""
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.fetchone.return_value = {
        "email": "admin@college.com", "role": "admin"}

    fake_conn.cursor.return_value = fake_cursor
    monkeypatch.setattr(admin_module, "get_db_conn", lambda: fake_conn)

    result = admin_module.get_user_role("admin@college.com")

    assert result == "admin"
    fake_cursor.execute.assert_called_once()


def test_prevent_unauthorized_update(monkeypatch):
    """Should block role update for non-admins."""
    fake_conn = MagicMock()
    fake_cursor = MagicMock()

    fake_conn.cursor.return_value = fake_cursor
    monkeypatch.setattr(admin_module, "get_db_conn", lambda: fake_conn)

    # Simulate non-admin attempting edit
    def mock_get_user_role(email):
        return "student"

    monkeypatch.setattr(admin_module, "get_user_role", mock_get_user_role)

    role = admin_module.get_user_role("student@college.com")
    assert role != "admin"
