"""ITC-01: Admin integration test"""
import pytest
from unittest.mock import patch, MagicMock

@patch('src.dashboards.admin.get_conn')
@patch('src.dashboards.admin.st')
def test_itc_01_admin_integration(mock_st, mock_conn):
    """ITC-01: Admin dashboard integration"""
    from src.dashboards.admin import approve_user
    
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 1
    mock_db.cursor.return_value = mock_cursor
    mock_db.__enter__.return_value = mock_db
    mock_db.__exit__.return_value = None
    mock_conn.return_value = mock_db
    
    user = {
        'id': 1, 'username': 'test', 'password_hash': 'hash',
        'role': 'student', 'email': 'test@test.com',
        'full_name': 'Test User', 'course_id': 1
    }
    
    with patch.object(mock_st, 'success'), patch.object(mock_st, 'rerun'):
        approve_user(user)
        assert mock_cursor.execute.called
