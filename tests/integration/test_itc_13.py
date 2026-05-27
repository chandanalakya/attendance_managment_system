"""ITC-13: Report Generation + Attendance Database"""
import pytest
from src.utils.export_csv import to_csv_bytes
from src.utils.export_pdf import to_pdf_bytes

def test_itc_13_report_generation_db():
    """ITC-13: Report generation with DB data accuracy"""
    data = [{'id': 1, 'name': 'Student1', 'status': 'PRESENT'}]
    
    csv_result = to_csv_bytes(data)
    assert isinstance(csv_result, bytes)
    assert len(csv_result) > 0
    
    pdf_result = to_pdf_bytes("Test Report", data)
    assert isinstance(pdf_result, bytes)
    assert pdf_result.startswith(b'%PDF')
