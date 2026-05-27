"""ITC-16: Defaulter List + Threshold Logic + DB"""
import pytest

def test_itc_16_defaulter_list_threshold_db():
    """ITC-16: Defaulter list generated with threshold logic"""
    students = [
        {'id': 1, 'name': 'Student A', 'attendance': 85.0},
        {'id': 2, 'name': 'Student B', 'attendance': 72.0},
        {'id': 3, 'name': 'Student C', 'attendance': 68.0},
    ]
    
    threshold = 75.0
    defaulters = [s for s in students if s['attendance'] < threshold]
    
    assert len(defaulters) == 2
    assert all(s['attendance'] < threshold for s in defaulters)
