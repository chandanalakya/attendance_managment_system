"""Coverage tests for export_pdf module"""
import pytest
from src.utils.export_pdf import to_pdf_bytes

def test_to_pdf_bytes_empty():
    result = to_pdf_bytes("Empty Report", [])
    assert isinstance(result, bytes)
    assert result.startswith(b'%PDF')

def test_to_pdf_bytes_single_row():
    data = [{'id': 1, 'name': 'Test'}]
    result = to_pdf_bytes("Single Row Report", data)
    assert isinstance(result, bytes)
    assert result.startswith(b'%PDF')

def test_to_pdf_bytes_multiple_rows():
    data = [
        {'id': 1, 'name': 'Test1', 'value': 100},
        {'id': 2, 'name': 'Test2', 'value': 200},
        {'id': 3, 'name': 'Test3', 'value': 300}
    ]
    result = to_pdf_bytes("Multiple Rows Report", data)
    assert isinstance(result, bytes)
    assert result.startswith(b'%PDF')

def test_to_pdf_bytes_large_dataset():
    data = [{'id': i, 'details': f'Entry {i}'} for i in range(100)]
    result = to_pdf_bytes("Large Report", data)
    assert isinstance(result, bytes)
    assert result.startswith(b'%PDF')

def test_to_pdf_bytes_special_chars():
    data = [{'name': 'Test™', 'value': '€100'}]
    result = to_pdf_bytes("Special Chars Report", data)
    assert isinstance(result, bytes)
    assert result.startswith(b'%PDF')
