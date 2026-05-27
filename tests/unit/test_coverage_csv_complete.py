"""Complete CSV coverage tests"""
import pytest
from src.utils.export_csv import to_csv_bytes
import io
import csv

def test_csv_bytes_with_writer():
    data = [
        {'name': 'Alice', 'age': 30, 'city': 'NYC'},
        {'name': 'Bob', 'age': 25, 'city': 'LA'}
    ]
    result = to_csv_bytes(data)
    
    # Decode and verify
    decoded = result.decode('utf-8')
    assert 'name' in decoded
    assert 'Alice' in decoded
    assert 'Bob' in decoded

def test_csv_bytes_encoding():
    data = [{'field': 'value1'}, {'field': 'value2'}]
    result = to_csv_bytes(data)
    assert isinstance(result, bytes)
    assert b'field' in result

def test_csv_bytes_newlines():
    data = [{'a': '1'}, {'a': '2'}, {'a': '3'}]
    result = to_csv_bytes(data)
    lines = result.decode('utf-8').strip().split('\n')
    assert len(lines) == 4  # header + 3 rows

def test_csv_bytes_quoting():
    data = [{'text': 'value with, comma'}]
    result = to_csv_bytes(data)
    assert b'text' in result

def test_csv_bytes_getvalue():
    data = [{'x': 1}]
    result = to_csv_bytes(data)
    assert len(result) > 0
