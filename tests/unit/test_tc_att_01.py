"""TC-Att-01: Faculty marks attendance"""
import pytest
from unittest.mock import Mock
from src.models.attendance import add_attendance

@pytest.fixture
def mock_db():
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_cursor.lastrowid = 123
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn

def test_tc_att_01_faculty_marks_attendance(mock_db):
    """TC-Att-01: Faculty marks attendance"""
    result = add_attendance(
        mock_db,
        course_id=1,
        student_id=1,
        status="PRESENT",
        taken_by_user_id=1,
        ip_address="127.0.0.1",
        notes="Real-time attendance marking"
    )
    
    assert result == 123
    assert mock_db.commit.called
