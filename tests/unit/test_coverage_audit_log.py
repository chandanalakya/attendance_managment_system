"""Coverage tests for audit_log module"""
import pytest
from unittest.mock import Mock
from src.models.audit_log import log_action, log_security_event, fetch_logs

@pytest.fixture
def mock_db():
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_cursor.lastrowid = 1
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = (1,)
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn

def test_log_action_add(mock_db):
    result = log_action(mock_db, "ADD", None, 1, "127.0.0.1", "Test")
    assert result == 1

def test_log_action_edit(mock_db):
    result = log_action(mock_db, "EDIT", 1, 1, "127.0.0.1", "Test")
    assert result == 1

def test_log_action_delete(mock_db):
    result = log_action(mock_db, "DELETE", 1, 1, "127.0.0.1", "Test")
    assert result == 1

def test_log_action_invalid(mock_db):
    with pytest.raises(ValueError):
        log_action(mock_db, "INVALID", 1, 1, "127.0.0.1", "Test")

def test_log_action_no_attendance_id(mock_db):
    mock_db.cursor.return_value.fetchone.return_value = None
    result = log_action(mock_db, "EDIT", 999, 1, "127.0.0.1", "Test")
    assert result == 1

def test_log_security_event(mock_db):
    result = log_security_event(mock_db, "LOGIN_SUCCESS", 1, "127.0.0.1", "users", "SELECT", "Test")
    assert result == 1

def test_fetch_logs_no_filters(mock_db):
    result = fetch_logs(mock_db)
    assert isinstance(result, list)

def test_fetch_logs_with_start(mock_db):
    mock_db.cursor.return_value.fetchall.return_value = [(1, "ADD", 1, 1, "127.0.0.1", "Test", "2025-01-01")]
    result = fetch_logs(mock_db, start="2025-01-01")
    assert len(result) == 1

def test_fetch_logs_with_end(mock_db):
    result = fetch_logs(mock_db, end="2025-12-31")
    assert isinstance(result, list)

def test_fetch_logs_with_user_id(mock_db):
    result = fetch_logs(mock_db, user_id=1)
    assert isinstance(result, list)

def test_fetch_logs_with_course_id(mock_db):
    result = fetch_logs(mock_db, course_id=1)
    assert isinstance(result, list)

def test_fetch_logs_all_filters(mock_db):
    result = fetch_logs(mock_db, start="2025-01-01", end="2025-12-31", user_id=1, course_id=1)
    assert isinstance(result, list)
