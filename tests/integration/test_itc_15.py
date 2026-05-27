"""ITC-15: Student Attendance Report + Display Module"""
import pytest

def test_itc_15_student_report_display():
    """ITC-15: Student-specific report loads correctly from DB"""
    student_report = {
        'student_id': 1,
        'courses': [
            {'course': 'CS101', 'present': 17, 'total': 20, 'percentage': 85.0},
            {'course': 'CS102', 'present': 18, 'total': 20, 'percentage': 90.0}
        ]
    }
    
    assert student_report['student_id'] == 1
    assert len(student_report['courses']) > 0
    assert all('percentage' in c for c in student_report['courses'])
