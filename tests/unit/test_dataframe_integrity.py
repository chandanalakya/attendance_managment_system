import pandas as pd

def test_dataframe_structure():
    """✅ Ensure DataFrame schema matches expected attendance format."""
    df = pd.DataFrame({
        "student_id": ["S001"],
        "student_name": ["Aarav Sharma"],
        "course": ["Data Structures"],
        "faculty": ["Dr. John Smith"],
        "attendance_percentage": [82.5]
    })

    expected_cols = [
        "student_id", "student_name", "course", "faculty", "attendance_percentage"
    ]
    assert list(df.columns) == expected_cols
    assert df["attendance_percentage"].iloc[0] == 82.5
