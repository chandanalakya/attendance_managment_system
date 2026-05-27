"""Coverage tests for CSV logs functions"""
import pytest
from src.utils.export_csv import logs_to_csv, export_logs_csv
import os
import tempfile

def test_logs_to_csv_with_dicts():
    logs = [
        {'id': 1, 'user_id': 1, 'action': 'ADD', 'ip_address': '127.0.0.1', 'timestamp': '2025-01-01', 'metadata': 'test', 'immutable': True},
        {'id': 2, 'user_id': 2, 'action': 'EDIT', 'ip_address': '127.0.0.2', 'timestamp': '2025-01-02', 'metadata': 'test2', 'immutable': True}
    ]
    result = logs_to_csv(logs)
    assert 'id' in result
    assert 'user_id' in result
    assert 'ADD' in result
    assert 'EDIT' in result

def test_logs_to_csv_with_objects():
    class MockLog:
        def __init__(self, id, user_id, action, ip_address, timestamp, metadata, immutable):
            self.id = id
            self.user_id = user_id
            self.action = action
            self.ip_address = ip_address
            self.timestamp = timestamp
            self.metadata = metadata
            self.immutable = immutable
    
    logs = [
        MockLog(1, 1, 'ADD', '127.0.0.1', '2025-01-01', 'test', True),
        MockLog(2, 2, 'EDIT', '127.0.0.2', '2025-01-02', 'test2', True)
    ]
    result = logs_to_csv(logs)
    assert '1' in result
    assert 'ADD' in result

def test_logs_to_csv_empty():
    logs = []
    result = logs_to_csv(logs)
    assert 'id' in result
    assert 'user_id' in result

def test_export_logs_csv():
    logs = [{'id': 1, 'name': 'Test'}]
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as f:
        temp_path = f.name
    
    try:
        export_logs_csv(logs, temp_path)
        assert os.path.exists(temp_path)
        with open(temp_path, 'rb') as f:
            content = f.read()
            assert len(content) > 0
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
