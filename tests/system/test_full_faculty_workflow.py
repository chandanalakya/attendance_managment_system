# tests/system/test_full_faculty_workflow.py
from src.faculty_attendance import (
    get_faculty, get_classes, get_students, mark_attendance, get_attendance_records
)

def test_full_faculty_workflow(monkeypatch):
    """Simulate the entire faculty workflow with a fully-mocked DB connection."""

    mock_faculty = {"id": 1, "name": "John Smith"}
    mock_classes = [{"id": 101, "name": "B.Tech CSE - A"}]
    mock_students = [
        {"id": 1, "name": "Aarav Sharma"},
        {"id": 2, "name": "Isha Patel"},
        {"id": 3, "name": "Rahul Verma"},
    ]
    mock_records = [
        {"class_name": "B.Tech CSE - A", "student_name": "Aarav Sharma", "status": "Present"},
        {"class_name": "B.Tech CSE - A", "student_name": "Isha Patel", "status": "Absent"},
        {"class_name": "B.Tech CSE - A", "student_name": "Rahul Verma", "status": "Present"},
    ]

    # ---- complete mock connection ----
    class MockCursor:
        def execute(self, query, params=None):  # accept any SQL
            self.query, self.params = query, params
        def fetchone(self): return mock_faculty
        def fetchall(self):
            if "class" in self.query.lower(): return mock_classes
            if "student" in self.query.lower(): return mock_students
            if "attendance" in self.query.lower(): return mock_records
            return []
        def close(self): pass

    class MockConnection:
        def cursor(self, *a, **kw): return MockCursor()
        def commit(self): pass
        def rollback(self): pass
        def close(self): pass

    # patch DB connection so every function uses the mock
    monkeypatch.setattr("src.faculty_attendance.get_connection", lambda: MockConnection())

    # run full workflow
    faculty = get_faculty("john@college.edu", "john123")
    classes = get_classes(faculty["id"])
    students = get_students(classes[0]["id"])
    mark_attendance(classes[0]["id"], {s["id"]: True for s in students},
                    "2025-11-08", "09:00", "10:00")
    records = get_attendance_records(faculty["id"])

    # verify logic
    assert faculty["name"] == "John Smith"
    assert len(classes) == 1
    assert len(students) == 3
    assert len(records) == 3
