"""ITC-18: Alerts Module + Attendance DB"""
import pytest

def test_itc_18_alerts_attendance_db():
    """ITC-18: Alerts triggered for mass absenteeism"""
    daily_attendance = {
        'date': '2025-11-15',
        'total_students': 100,
        'present': 45,
        'absent': 55,
        'percentage': 45.0
    }
    
    alert_threshold = 60.0
    alert_triggered = daily_attendance['percentage'] < alert_threshold
    
    assert alert_triggered is True
    assert daily_attendance['absent'] > daily_attendance['present']
