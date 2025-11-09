import pandas as pd
from src.login_system import load_attendance

class MockConn:
    def close(self): pass

def test_load_attendance(monkeypatch):
    """✅ Check if attendance loads correctly (mocked DB)."""
    fake_df = pd.DataFrame({
        "student_id": ["S001"],
        "student_name": ["Aarav Sharma"],
        "course": ["Data Structures"],
        "faculty": ["faculty1"],
        "attendance_percentage": [85.0]
    })

    monkeypatch.setattr("src.login_system.get_connection", lambda: MockConn())
    monkeypatch.setattr(pd, "read_sql", lambda q, c: fake_df)

    df = load_attendance()
    assert not df.empty
    assert "student_id" in df.columns
    assert df.iloc[0]["student_name"] == "Aarav Sharma"
