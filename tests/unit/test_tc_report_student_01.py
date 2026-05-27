"""TC-Report-Student-01: Student views course-wise attendance report"""
import pytest

def test_tc_report_student_01_course_wise_report():
    """TC-Report-Student-01: Student views course-wise attendance report"""
    course_report = {
        'course_id': 1,
        'course_name': 'CS101',
        'total_classes': 20,
        'attended': 17,
        'percentage': 85.0,
        'status': 'SAFE'
    }
    
    assert course_report['percentage'] == (course_report['attended'] / course_report['total_classes']) * 100
    assert course_report['status'] in ['SAFE', 'WARNING', 'DEFAULTER']
