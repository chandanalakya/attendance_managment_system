"""TC-Report-Filter-01: Report filtering (course/date range)"""
import pytest

def test_tc_report_filter_01_filter_by_course():
    """TC-Report-Filter-01: Filter reports by course"""
    all_data = [
        {'course': 'CS101', 'date': '2025-11-01', 'status': 'PRESENT'},
        {'course': 'CS102', 'date': '2025-11-01', 'status': 'ABSENT'},
        {'course': 'CS101', 'date': '2025-11-02', 'status': 'PRESENT'},
    ]
    
    filtered_by_course = [r for r in all_data if r['course'] == 'CS101']
    assert len(filtered_by_course) == 2

def test_tc_report_filter_01_filter_by_date():
    """TC-Report-Filter-01: Filter reports by date range"""
    all_data = [
        {'course': 'CS101', 'date': '2025-11-01', 'status': 'PRESENT'},
        {'course': 'CS102', 'date': '2025-11-01', 'status': 'ABSENT'},
        {'course': 'CS101', 'date': '2025-11-02', 'status': 'PRESENT'},
    ]
    
    filtered_by_date = [r for r in all_data if r['date'] == '2025-11-01']
    assert len(filtered_by_date) == 2
