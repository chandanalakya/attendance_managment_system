"""Coverage tests for attendance module"""
import pytest
from unittest.mock import Mock
from src.models.attendance import add_attendance, edit_attendance, delete_attendance, attempt_modify_audit_logs
import mysql.connector

@pytest.fixture
def mock_db():
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_cursor.lastrowid = 1
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn

def test_add_attendance_with_notes(mock_db):
    result = add_attendance(mock_db, course_id=1, student_id=1, status="PRESENT", taken_by_user_id=1, ip_address="127.0.0.1", notes="Test")
    assert result == 1

def test_add_attendance_without_notes(mock_db):
    result = add_attendance(mock_db, course_id=1, student_id=1, status="PRESENT", taken_by_user_id=1, ip_address="127.0.0.1")
    assert result == 1

def test_add_attendance_rollback(mock_db):
    mock_db.cursor.return_value.execute.side_effect = Exception("Error")
    with pytest.raises(Exception):
        add_attendance(mock_db, course_id=1, student_id=1, status="PRESENT", taken_by_user_id=1, ip_address="127.0.0.1")
    assert mock_db.rollback.called

def test_edit_attendance_with_notes(mock_db):
    edit_attendance(mock_db, attendance_id=1, new_status="ABSENT", user_id=1, ip_address="127.0.0.1", notes="Test")
    assert mock_db.commit.called

def test_edit_attendance_without_notes(mock_db):
    edit_attendance(mock_db, attendance_id=1, new_status="ABSENT", user_id=1, ip_address="127.0.0.1")
    assert mock_db.commit.called

def test_edit_attendance_rollback(mock_db):
    mock_db.cursor.return_value.execute.side_effect = Exception("Error")
    with pytest.raises(Exception):
        edit_attendance(mock_db, attendance_id=1, new_status="ABSENT", user_id=1, ip_address="127.0.0.1")
    assert mock_db.rollback.called

def test_delete_attendance(mock_db):
    delete_attendance(mock_db, attendance_id=1, user_id=1, ip_address="127.0.0.1")
    assert mock_db.commit.called

def test_delete_attendance_rollback(mock_db):
    mock_db.cursor.return_value.execute.side_effect = Exception("Error")
    with pytest.raises(Exception):
        delete_attendance(mock_db, attendance_id=1, user_id=1, ip_address="127.0.0.1")
    assert mock_db.rollback.called

def test_attempt_modify_audit_logs_update(mock_db):
    mock_db.cursor.return_value.execute.side_effect = mysql.connector.Error("Permission denied")
    with pytest.raises(mysql.connector.Error):
        attempt_modify_audit_logs(mock_db, operation="UPDATE", user_id=1, ip_address="127.0.0.1")

def test_attempt_modify_audit_logs_delete(mock_db):
    mock_db.cursor.return_value.execute.side_effect = mysql.connector.Error("Permission denied")
    with pytest.raises(mysql.connector.Error):
        attempt_modify_audit_logs(mock_db, operation="DELETE", user_id=1, ip_address="127.0.0.1")
