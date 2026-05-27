"""ITC-06: Login + Account Lockout"""
import pytest
from unittest.mock import patch, MagicMock

@patch('src.auth.authentication.get_conn')
@patch('src.auth.authentication.check_account_lock')
@patch('src.auth.authentication.increment_failed_attempts')
def test_itc_06_login_account_lockout(mock_increment, mock_lock, mock_conn):
    """ITC-06: Login with account lockout after 5 failed attempts"""
    from src.auth.authentication import authenticate
    
    mock_lock.return_value = False
    mock_increment.return_value = "Invalid credentials. 4 attempts remaining."
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_db.cursor.return_value = mock_cursor
    mock_db.__enter__.return_value = mock_db
    mock_db.__exit__.return_value = None
    mock_conn.return_value = mock_db
    
    user, error = authenticate('admin', 'wrongpassword', 'admin')
    
    assert user is None
    assert "Invalid credentials" in error
    mock_increment.assert_called_once()
