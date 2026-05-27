"""Coverage tests for security module"""
import pytest
from unittest.mock import patch, Mock
from src.utils.security import hash_password, check_account_lock, increment_failed_attempts, reset_failed_attempts, get_lock_remaining_time

def test_hash_password():
    password = "test123"
    hashed = hash_password(password)
    assert len(hashed) == 64
    assert hashed != password

@patch('src.utils.security.st')
def test_check_account_lock_not_locked(mock_st):
    mock_st.session_state.locked_until = None
    result = check_account_lock()
    assert result is False

@patch('src.utils.security.st')
@patch('src.utils.security.time')
def test_check_account_lock_locked(mock_time, mock_st):
    mock_time.time.return_value = 1000
    mock_st.session_state.locked_until = 2000
    result = check_account_lock()
    assert result is True

@patch('src.utils.security.st')
@patch('src.utils.security.time')
def test_check_account_lock_expired(mock_time, mock_st):
    mock_time.time.return_value = 2000
    mock_st.session_state.locked_until = 1000
    result = check_account_lock()
    assert result is False

@patch('src.utils.security.st')
def test_get_lock_remaining_time_no_lock(mock_st):
    mock_st.session_state.locked_until = None
    mins, secs = get_lock_remaining_time()
    assert mins == 0
    assert secs == 0

@patch('src.utils.security.st')
@patch('src.utils.security.time')
def test_get_lock_remaining_time_with_lock(mock_time, mock_st):
    mock_time.time.return_value = 1000
    mock_st.session_state.locked_until = 1180
    mins, secs = get_lock_remaining_time()
    assert mins == 3
    assert secs == 0

@patch('src.utils.security.st')
def test_increment_failed_attempts_first(mock_st):
    mock_st.session_state.failed_attempts = 0
    result = increment_failed_attempts()
    assert "4 attempts remaining" in result

@patch('src.utils.security.st')
@patch('src.utils.security.time')
def test_increment_failed_attempts_locked(mock_time, mock_st):
    mock_time.time.return_value = 1000
    mock_st.session_state.failed_attempts = 4
    result = increment_failed_attempts()
    assert "locked" in result.lower()

@patch('src.utils.security.st')
def test_reset_failed_attempts(mock_st):
    reset_failed_attempts()
    assert mock_st.session_state.failed_attempts == 0
    assert mock_st.session_state.locked_until is None
