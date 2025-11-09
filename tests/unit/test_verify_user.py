from src.login_system import verify_user

class MockCursor:
    def __init__(self, user_data=None):
        self.user_data = user_data or {
            "username": "faculty1",
            "password_hash": "abc",
            "failed_attempts": 0,
            "is_locked": False,
            "last_failed_time": None,
            "role": "Faculty"
        }
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchone(self):
        return self.user_data

    def close(self): pass


class MockConn:
    def __init__(self, cursor_data=None):
        self.cursor_data = cursor_data

    def cursor(self, *args, **kwargs):
        return MockCursor(self.cursor_data)

    def commit(self): pass
    def close(self): pass


def test_verify_user_success(monkeypatch):
    """✅ Simulate successful login for faculty."""
    monkeypatch.setattr("src.login_system.get_connection", lambda: MockConn())
    monkeypatch.setattr("src.login_system.hash_password", lambda p: "abc")

    result, role = verify_user("faculty1", "faculty123")
    assert result is True
    assert role == "Faculty"


def test_verify_user_wrong_password(monkeypatch):
    """❌ Simulate wrong password attempt."""
    data = {"username": "faculty1", "password_hash": "xyz", "failed_attempts": 1, "is_locked": False, "role": "Faculty"}
    monkeypatch.setattr("src.login_system.get_connection", lambda: MockConn(data))
    monkeypatch.setattr("src.login_system.hash_password", lambda p: "wrong")

    result, msg = verify_user("faculty1", "bad")
    assert result is False
    assert "Attempts left" in msg
