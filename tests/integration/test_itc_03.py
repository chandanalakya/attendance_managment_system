"""ITC-03: Faculty dashboard flow integration test"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime

@patch('src.dashboards.faculty.get_conn')
@patch('src.dashboards.faculty.st')
def test_itc_03_faculty_dashboard_flow(mock_st, mock_conn):
    """ITC-03: Faculty dashboard complete flow"""
    from src.dashboards.faculty import submit_attendance
    
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (0,)
    mock_db.cursor.return_value = mock_cursor
    mock_db.__enter__.return_value = mock_db
    mock_db.__exit__.return_value = None
    mock_conn.return_value = mock_db
    mock_st.session_state.user_id = 1
    
    attendance_data = [
        {'student_id': 1, 'status': 'PRESENT'},
        {'student_id': 2, 'status': 'ABSENT'}
    ]
    
    with patch.object(mock_st, 'toast'), patch.object(mock_st, 'balloons'):
        submit_attendance(attendance_data, 1, date.today(), datetime.now().time())
        assert mock_cursor.execute.called
