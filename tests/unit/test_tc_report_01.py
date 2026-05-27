"""TC-Report-01: Faculty generates attendance report (CSV/PDF)"""
import pytest
from src.utils.export_csv import to_csv_bytes
from src.utils.export_pdf import to_pdf_bytes

def test_tc_report_01_generate_csv_report():
    """TC-Report-01: Generate CSV attendance report"""
    report_data = [
        {'student_id': 1, 'name': 'John Doe', 'present': 17, 'absent': 3, 'percentage': 85.0},
        {'student_id': 2, 'name': 'Jane Smith', 'present': 18, 'absent': 2, 'percentage': 90.0}
    ]
    
    csv_result = to_csv_bytes(report_data)
    assert isinstance(csv_result, bytes)
    assert len(csv_result) > 0

def test_tc_report_01_generate_pdf_report():
    """TC-Report-01: Generate PDF attendance report"""
    report_data = [
        {'student_id': 1, 'name': 'John Doe', 'present': 17, 'absent': 3, 'percentage': 85.0}
    ]
    
    pdf_result = to_pdf_bytes("Attendance Report", report_data)
    assert isinstance(pdf_result, bytes)
    assert pdf_result.startswith(b'%PDF')
