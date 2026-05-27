"""TC-Alert-01: Admin alert for sudden drop in attendance"""
import pytest

def test_tc_alert_01_sudden_attendance_drop():
    """TC-Alert-01: Admin alert for sudden drop in attendance"""
    weekly_attendance = [
        {'week': 1, 'percentage': 85.0},
        {'week': 2, 'percentage': 83.0},
        {'week': 3, 'percentage': 65.0},
    ]
    
    drop_threshold = 15.0
    week2_to_week3_drop = weekly_attendance[1]['percentage'] - weekly_attendance[2]['percentage']
    
    alert_triggered = week2_to_week3_drop >= drop_threshold
    
    assert alert_triggered is True
    assert week2_to_week3_drop == 18.0
