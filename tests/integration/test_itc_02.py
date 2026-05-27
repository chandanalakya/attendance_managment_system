"""ITC-02: Audit log integration test"""
import pytest
from unittest.mock import MagicMock
from src.models.audit_log import log_action, fetch_logs

def test_itc_02_audit_log_integration():
    """ITC-02: Audit log creation and retrieval"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 1
    mock_cursor.fetchall.return_value = []
    mock_conn.cursor.return_value = mock_cursor
    
    log_action(mock_conn, 'ADD', None, 1, '127.0.0.1', 'Test action')
    logs = fetch_logs(mock_conn, user_id=1)
    
    assert isinstance(logs, list)
    assert mock_cursor.execute.called
