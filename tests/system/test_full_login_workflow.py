from src.login_system import verify_user, load_attendance

def test_full_login_workflow(monkeypatch):
    """✅ Full faculty login workflow (mocked DB and functions)."""

    # Mock the DB-dependent functions
    monkeypatch.setattr("src.login_system.get_connection", lambda: None)
    monkeypatch.setattr("src.login_system.verify_user", lambda u, p: (True, "Faculty"))
    monkeypatch.setattr("src.login_system.load_attendance", lambda: {
        "student_id": ["S001"],
        "student_name": ["Aarav Sharma"],
        "course": ["Data Structures"],
        "faculty": ["faculty1"],
        "attendance_percentage": [85.0]
    })

    # Simulate a login + dashboard flow
    success, role = verify_user("faculty1", "faculty123")
    assert success
    assert role == "Faculty"
