from src.faculty_attendance import (
    get_faculty, get_classes, get_students, mark_attendance, get_attendance_records
)

def test_full_faculty_workflow(monkeypatch):
    """Full faculty login → class → students → attendance → view records (mocked DB)."""

    # Mock data for the workflow
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

    # ✅ Mock DB connection + cursor behavior
    class MockCursor:
        def execute(self, query, params=None):
            self.query = query
            self.params = params

        def fetchone(self):
            if "faculty" in self.query.lower():
                return mock_faculty
            return None

        def fetchall(self):
            if "class" in self.query.lower():
                return mock_classes
            if "student" in self.query.lower():
                return mock_students
            if "attendance" in self.query.lower():
                return mock_records
            return []

        def close(self): pass

    class MockConnection:
        def cursor(self, *args, **kwargs): return MockCursor()
        def close(self): pass

    # ✅ Patch connection
    monkeypatch.setattr("src.faculty_attendance.get_connection", lambda: MockConnection())

    # Simulate full workflow
    faculty = get_faculty("john@college.edu", "john123")
    classes = get_classes(faculty["id"])
    assert classes, "Classes list should not be empty"
    students = get_students(classes[0]["id"])
    assert students, "Students list should not be empty"
    mark_attendance(classes[0]["id"], {s["id"]: True for s in students}, "2025-11-08", "09:00", "10:00")
    records = get_attendance_records(faculty["id"])

    # ✅ Validate results
    assert faculty["name"] == "John Smith"
    assert len(classes) == 1
    assert len(students) == 3
    assert len(records) == 3
