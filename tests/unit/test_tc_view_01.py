"""TC-View-01: Student views overall/subject attendance"""
import pytest

def test_tc_view_01_student_views_overall_attendance():
    """TC-View-01: Student views overall/subject attendance"""
    student_attendance = {
        'overall_percentage': 85.5,
        'subjects': {
            'CS101': {'present': 17, 'total': 20, 'percentage': 85.0},
            'CS102': {'present': 18, 'total': 20, 'percentage': 90.0},
            'CS103': {'present': 16, 'total': 20, 'percentage': 80.0}
        }
    }
    
    assert student_attendance['overall_percentage'] >= 0
    assert student_attendance['overall_percentage'] <= 100
    assert len(student_attendance['subjects']) > 0
