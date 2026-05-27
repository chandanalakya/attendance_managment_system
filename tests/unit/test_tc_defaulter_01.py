"""TC-Defaulter-01: Generate defaulter list (<75%)"""
import pytest

def test_tc_defaulter_01_generate_defaulter_list():
    """TC-Defaulter-01: Generate defaulter list"""
    students = [
        {'id': 1, 'name': 'Student A', 'attendance': 85.0},
        {'id': 2, 'name': 'Student B', 'attendance': 72.0},
        {'id': 3, 'name': 'Student C', 'attendance': 68.0},
        {'id': 4, 'name': 'Student D', 'attendance': 90.0},
    ]
    
    threshold = 75.0
    defaulters = [s for s in students if s['attendance'] < threshold]
    
    assert len(defaulters) == 2
    assert all(s['attendance'] < threshold for s in defaulters)
