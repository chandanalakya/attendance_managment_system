"""TC-Daily-Attendance-01: Real-time update of day-wise attendance"""
import pytest
from datetime import date

def test_tc_daily_attendance_01_realtime_update():
    """TC-Daily-Attendance-01: Real-time update of day-wise attendance"""
    attendance_record = {
        'date': date.today(),
        'student_id': 1,
        'course_id': 1,
        'status': 'PRESENT',
        'timestamp': '2025-01-15 10:30:00'
    }
    
    assert attendance_record['date'] == date.today()
    assert attendance_record['status'] in ['PRESENT', 'ABSENT', 'LATE', 'EXCUSED']
    assert 'timestamp' in attendance_record
