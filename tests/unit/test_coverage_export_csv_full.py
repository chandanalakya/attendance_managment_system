"""Full coverage tests for export_csv module"""
import pytest
from src.utils.export_csv import to_csv_bytes

def test_to_csv_bytes_with_data():
    data = [
        {'id': 1, 'name': 'Test1', 'value': 100},
        {'id': 2, 'name': 'Test2', 'value': 200}
    ]
    result = to_csv_bytes(data)
    assert isinstance(result, bytes)
    assert b'id' in result
    assert b'name' in result

def test_to_csv_bytes_large_data():
    data = [{'id': i, 'value': i*10} for i in range(100)]
    result = to_csv_bytes(data)
    assert isinstance(result, bytes)
    assert len(result) > 0
