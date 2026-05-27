"""TC-Audit-01: Audit logging for attendance edits"""
import pytest
from unittest.mock import Mock
from src.models.audit_log import log_action

@pytest.fixture
def mock_db():
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_cursor.lastrowid = 456
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn

def test_tc_audit_01_audit_logging(mock_db):
    """TC-Audit-01: Audit logging for attendance edits"""
    result = log_action(
        mock_db,
        action_type="EDIT",
        attendance_id=1,
        user_id=1,
        ip_address="127.0.0.1",
        details="Changed status from PRESENT to ABSENT"
    )
    
    assert result == 456
    assert mock_db.commit.called
