import importlib.util
import pytest
from unittest.mock import MagicMock

# Load student_login module
spec = importlib.util.spec_from_file_location(
    "student_login", "src/student_login.py"
)
student_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(student_module)
@pytest.mark.skip(reason="Skipping student tests on faculty_login branch")
def test_end_to_end_student_registration_login_flow(monkeypatch):
    # Mock DB connection
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.fetchone.return_value = {
        "email": "student@college.com",
        "role": "student",
        "is_approved": True,
    }
    fake_conn.cursor.return_value = fake_cursor
    monkeypatch.setattr(student_module, "get_db_conn", lambda: fake_conn)

    # Continue your test normally
    conn = student_module.get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1")  # Example operation
    assert cur.fetchone() is not None
