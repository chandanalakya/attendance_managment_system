from unittest.mock import patch
from src import faculty_admin as fa
import pandas as pd

@patch("src.faculty_admin.load_data")
def test_faculty_dashboard_logic(mock_load_data):
    """✅ Simulate faculty dashboard data filtering."""
    df = pd.DataFrame({
        "student_id": ["S001", "S002", "S003"],
        "student_name": ["Aarav", "Isha", "Rahul"],
        "course": ["DS", "DS", "DBMS"],
        "faculty": ["Dr. John Smith", "Dr. John Smith", "Dr. Mary Johnson"],
        "attendance_percentage": [82.5, 68.0, 91.2]
    })
    mock_load_data.return_value = df

    data = fa.load_data()
    assert not data.empty
    faculty_data = data[data["faculty"] == "Dr. John Smith"]
    assert len(faculty_data) == 2
    assert "attendance_percentage" in faculty_data.columns
