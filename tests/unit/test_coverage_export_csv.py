"""Coverage tests for export_csv module"""
import pytest
from src.utils.export_csv import to_csv_bytes

def test_to_csv_bytes_empty():
    result = to_csv_bytes([])
    assert result == b''

def test_to_csv_bytes_single_row():
    data = [{'id': 1, 'name': 'Test'}]
    result = to_csv_bytes(data)
    assert isinstance(result, bytes)
    assert len(result) > 0

def test_to_csv_bytes_multiple_rows():
    data = [
        {'id': 1, 'name': 'Test1'},
        {'id': 2, 'name': 'Test2'},
        {'id': 3, 'name': 'Test3'}
    ]
    result = to_csv_bytes(data)
    assert isinstance(result, bytes)
    assert len(result) > 0

def test_to_csv_bytes_special_chars():
    data = [
        {'field': 'comma,test'},
        {'field': 'quote"test'},
        {'field': 'newline\ntest'}
    ]
    result = to_csv_bytes(data)
    assert isinstance(result, bytes)

def test_to_csv_bytes_unicode():
    data = [{'name': 'Test™', 'value': '€100'}]
    result = to_csv_bytes(data)
    assert isinstance(result, bytes)
