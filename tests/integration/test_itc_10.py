"""ITC-10: Faculty Edit Attendance + Audit Logging"""
import pytest
from unittest.mock import Mock
from src.models.attendance import edit_attendance

def test_itc_10_edit_attendance_audit_logging():
    """ITC-10: Faculty edits attendance with audit log entry"""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    
    edit_attendance(
        mock_conn,
        attendance_id=1,
        new_status="ABSENT",
        user_id=1,
        ip_address="127.0.0.1",
        notes="Medical certificate provided"
    )
    
    assert mock_cursor.execute.call_count == 2
    assert mock_conn.commit.called
