"""ITC-05: Login + Role-Based Access"""
import pytest
from unittest.mock import patch, MagicMock

@patch('src.auth.authentication.get_conn')
@patch('src.auth.authentication.check_account_lock')
@patch('src.auth.authentication.reset_failed_attempts')
def test_itc_05_login_role_based_access(mock_reset, mock_lock, mock_conn):
    """ITC-05: Login with role-based access"""
    from src.auth.authentication import authenticate
    
    mock_lock.return_value = False
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1, 'admin', 'admin')
    mock_db.cursor.return_value = mock_cursor
    mock_db.__enter__.return_value = mock_db
    mock_db.__exit__.return_value = None
    mock_conn.return_value = mock_db
    
    user, error = authenticate('admin', 'admin123', 'admin')
    
    assert user is not None
    assert user['role'] == 'admin'
    assert error is None
