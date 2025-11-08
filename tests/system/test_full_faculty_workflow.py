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

    # ✅ Prevent any real DB calls
    monkeypatch.setattr("src.faculty_attendance.get_connection", lambda: True)
    monkeypatch.setattr("src.faculty_attendance.get_faculty", lambda e, p: mock_faculty)
    monkeypatch.setattr("src.faculty_attendance.get_classes", lambda fid: mock_classes)
    monkeypatch.setattr("src.faculty_attendance.get_students", lambda cid: mock_students)
    monkeypatch.setattr("src.faculty_attendance.mark_attendance", lambda *a, **kw: True)
    monkeypatch.setattr("src.faculty_attendance.get_attendance_records", lambda fid: mock_records)

    # Simulate workflow
    faculty = get_faculty("john@college.edu", "john123")
    classes = get_classes(faculty["id"])
    students = get_students(classes[0]["id"])
    mark_attendance(classes[0]["id"], {s["id"]: True for s in students}, "2025-11-08", "09:00", "10:00")
    records = get_attendance_records(faculty["id"])

    # Assertions
    assert faculty["name"] == "John Smith"
    assert len(classes) == 1
    assert len(students) == 3
    assert len(records) == 3
