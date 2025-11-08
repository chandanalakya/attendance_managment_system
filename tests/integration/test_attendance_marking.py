from src.faculty_attendance import mark_attendance

def test_mark_attendance(monkeypatch):
    """Ensure attendance is inserted properly."""
    executed = []

    class MockCursor:
        def execute(self, query, params): executed.append(params)
    class MockConn:
        def cursor(self): return MockCursor()
        def commit(self): pass
        def close(self): pass

    monkeypatch.setattr("src.faculty_attendance.get_connection", lambda: MockConn())

    attendance_dict = {1: True, 2: False}
    mark_attendance(101, attendance_dict, "2025-11-08", "09:00:00", "10:00:00")

    assert len(executed) == 2
    assert executed[0][1] == 101  # class_id check
