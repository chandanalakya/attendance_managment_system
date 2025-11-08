from src.faculty_attendance import get_faculty

def test_get_faculty(monkeypatch):
    """Test faculty login returns correct data."""
    mock_faculty = {"id": 1, "name": "John Smith"}

    class MockCursor:
        def execute(self, query, params): pass
        def fetchone(self): return mock_faculty
    class MockConn:
        def cursor(self, dictionary=True): return MockCursor()
        def close(self): pass

    monkeypatch.setattr("src.faculty_attendance.get_connection", lambda: MockConn())
    result = get_faculty("john@college.edu", "john123")
    assert result["name"] == "John Smith"
