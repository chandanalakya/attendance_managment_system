from src.faculty_attendance import get_students

def test_get_students(monkeypatch):
    """Verify get_students returns list of students for a class."""
    mock_students = [
        {"id": 1, "name": "Aarav Sharma"},
        {"id": 2, "name": "Isha Patel"}
    ]

    class MockCursor:
        def execute(self, query, params): pass
        def fetchall(self): return mock_students
    class MockConn:
        def cursor(self, dictionary=True): return MockCursor()
        def close(self): pass

    monkeypatch.setattr("src.faculty_attendance.get_connection", lambda: MockConn())
    data = get_students(1)
    assert len(data) == 2
    assert data[0]["name"] == "Aarav Sharma"
