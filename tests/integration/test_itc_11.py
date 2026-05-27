"""ITC-11: Attendance Update + Student Dashboard Sync"""
import pytest
from unittest.mock import patch, MagicMock

@patch('src.dashboards.student.get_conn')
@patch('src.dashboards.student.st')
def test_itc_11_attendance_update_student_sync(mock_st, mock_conn):
    """ITC-11: Attendance update syncs to student dashboard"""
    from src.dashboards.student import submit_correction_request
    
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.cursor.return_value = mock_cursor
    mock_db.__enter__.return_value = mock_db
    mock_db.__exit__.return_value = None
    mock_conn.return_value = mock_db
    mock_st.session_state.user_id = 1
    
    record = {'id': 1, 'status': 'absent'}
    
    with patch.object(mock_st, 'toast'):
        submit_correction_request(record, 'PRESENT', 'I was present')
        assert mock_cursor.execute.called
