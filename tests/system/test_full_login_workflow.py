from src import login_system

def test_full_login_workflow(monkeypatch):
    """✅ Full faculty login workflow simulation (completely mocked)."""

    # Mock the DB connection so it never tries to connect
    monkeypatch.setattr(login_system, "get_connection", lambda: None)

    # Mock verify_user to bypass DB logic
    def mock_verify_user(username, password):
        return True, "Faculty"

    # Mock load_attendance to simulate returned data
    def mock_load_attendance():
        return {
            "student_id": ["S001"],
            "student_name": ["Aarav Sharma"],
            "course": ["Data Structures"],
            "faculty": ["faculty1"],
            "attendance_percentage": [85.0]
        }

    monkeypatch.setattr(login_system, "verify_user", mock_verify_user)
    monkeypatch.setattr(login_system, "load_attendance", mock_load_attendance)

    # Simulate full login + dashboard behavior
    success, role = login_system.verify_user("faculty1", "faculty123")
    assert success is True
    assert role == "Faculty"

    data = login_system.load_attendance()
    assert data["student_name"][0] == "Aarav Sharma"
    assert data["attendance_percentage"][0] == 85.0
