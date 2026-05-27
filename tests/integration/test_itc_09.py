"""ITC-09: Faculty Mark Attendance + Database Update"""
import pytest
from unittest.mock import Mock
from src.models.attendance import add_attendance

def test_itc_09_mark_attendance_db_update():
    """ITC-09: Faculty marks attendance with instant DB storage"""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_cursor.lastrowid = 123
    mock_conn.cursor.return_value = mock_cursor
    
    result = add_attendance(
        mock_conn,
        course_id=1,
        student_id=1,
        status="PRESENT",
        taken_by_user_id=1,
        ip_address="127.0.0.1"
    )
    
    assert result == 123
    assert mock_conn.commit.called
