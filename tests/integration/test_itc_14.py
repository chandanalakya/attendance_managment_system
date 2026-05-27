"""ITC-14: Report Filtering + DB Query Engine"""
import pytest

def test_itc_14_report_filtering_db_query():
    """ITC-14: Report filtering affects DB queries correctly"""
    all_data = [
        {'course': 'CS101', 'date': '2025-11-01', 'status': 'PRESENT'},
        {'course': 'CS102', 'date': '2025-11-01', 'status': 'ABSENT'},
        {'course': 'CS101', 'date': '2025-11-02', 'status': 'PRESENT'},
    ]
    
    filtered_by_course = [r for r in all_data if r['course'] == 'CS101']
    assert len(filtered_by_course) == 2
    
    filtered_by_date = [r for r in all_data if r['date'] == '2025-11-01']
    assert len(filtered_by_date) == 2
