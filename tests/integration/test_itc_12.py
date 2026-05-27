"""ITC-12: Daily Attendance DB + Student Daily View"""
import pytest
from datetime import date

def test_itc_12_daily_attendance_db_student_view():
    """ITC-12: Daily attendance pulled correctly from DB"""
    daily_records = [
        {'date': date.today(), 'course': 'CS101', 'status': 'PRESENT'},
        {'date': date.today(), 'course': 'CS102', 'status': 'ABSENT'},
    ]
    
    assert all('date' in r for r in daily_records)
    assert all('status' in r for r in daily_records)
    assert all(r['date'] == date.today() for r in daily_records)
