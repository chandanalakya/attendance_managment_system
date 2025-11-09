import importlib.util
from unittest.mock import MagicMock

spec = importlib.util.spec_from_file_location("faculty_login", "src/faculty_login.py")
faculty_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(faculty_module)

def test_faculty_find_user_by_email(monkeypatch):
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.fetchone.return_value = {"email": "faculty@college.com", "role": "faculty", "is_approved": True}

    fake_conn.cursor.return_value = fake_cursor
    monkeypatch.setattr(faculty_module, "get_db_conn", lambda: fake_conn)

    result = faculty_module.find_user_by_email("faculty@college.com")

    assert result["email"] == "faculty@college.com"
    fake_cursor.execute.assert_called_once()
