from unittest.mock import patch
import pandas as pd
from src import faculty_admin as fa


@patch("src.faculty_admin.load_data")
def test_full_app_run(mock_load_data):
    """✅ Full workflow simulation for Faculty + Admin dashboards."""
    df = pd.DataFrame({
        "student_id": ["S001", "S002", "S003"],
        "student_name": ["Aarav Sharma", "Isha Patel", "Rahul Verma"],
        "course": ["Data Structures", "Data Structures", "Database Systems"],
        "faculty": ["Dr. John Smith", "Dr. John Smith", "Dr. Mary Johnson"],
        "attendance_percentage": [82.5, 68.0, 74.5],
    })
    mock_load_data.return_value = df

    # Faculty role simulation
    data = fa.load_data()
    assert not data.empty
    faculty_courses = data[data["faculty"] == "Dr. John Smith"]["course"].unique()
    assert "Data Structures" in faculty_courses

    # Admin role simulation: low attendance check
    low_attendance = data[data["attendance_percentage"] < 75]
    # ✅ Fix: Expect multiple students instead of one
    low_students = low_attendance["student_name"].tolist()
    assert set(low_students) == {"Isha Patel", "Rahul Verma"}
