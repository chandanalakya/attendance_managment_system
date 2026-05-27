"""ITC-04: Faculty DB integration test"""
import pytest
from unittest.mock import patch, MagicMock

@patch('src.dashboards.faculty.get_conn')
@patch('src.dashboards.faculty.st')
def test_itc_04_faculty_db_integration(mock_st, mock_conn):
    """ITC-04: Faculty database integration"""
    from src.dashboards.faculty import submit_edit_request
    
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.cursor.return_value = mock_cursor
    mock_db.__enter__.return_value = mock_db
    mock_db.__exit__.return_value = None
    mock_conn.return_value = mock_db
    mock_st.session_state.user_id = 1
    
    record = {'id': 1, 'status': 'absent'}
    
    with patch.object(mock_st, 'toast'):
        submit_edit_request(record, 'PRESENT', 'Valid justification')
        assert mock_cursor.execute.called
