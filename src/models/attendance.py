"""Attendance management models."""
import mysql.connector
from typing import Optional
from src.models.audit_log import log_action, log_security_event


def add_attendance(
    conn,
    *,
    course_id: int,
    student_id: int,
    status: str,
    taken_by_user_id: int,
    ip_address: str,
    notes: str = "",
    date: str = None,
) -> int:
    """Add new attendance record."""
    cur = conn.cursor()
    try:
        # Insert attendance record
        if date is None:
            cur.execute(
                """
                INSERT INTO attendance (course_id, student_id, date, status, taken_by_user_id, notes)
                VALUES (%s, %s, CURDATE(), %s, %s, %s)
                """,
                (course_id, student_id, status, taken_by_user_id, notes),
            )
        else:
            cur.execute(
                """
                INSERT INTO attendance (course_id, student_id, date, status, taken_by_user_id, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (course_id, student_id, date, status, taken_by_user_id, notes),
            )
        attendance_id = cur.lastrowid
        
        # Insert audit log in same transaction
        cur.execute(
            "INSERT INTO audit_logs (action_type, attendance_id, user_id, ip_address, details) VALUES (%s, %s, %s, %s, %s)",
            ("ADD", attendance_id, taken_by_user_id, ip_address, f"status={status}")
        )
        
        conn.commit()
        return attendance_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()


def edit_attendance(
    conn,
    *,
    attendance_id: int,
    new_status: str,
    user_id: int,
    ip_address: str,
    notes: str = "",
) -> None:
    """Edit existing attendance record."""
    cur = conn.cursor()
    try:
        # Update attendance record
        cur.execute(
            "UPDATE attendance SET status = %s, notes = %s WHERE id = %s",
            (new_status, notes, attendance_id),
        )
        
        # Insert audit log in same transaction
        cur.execute(
            "INSERT INTO audit_logs (action_type, attendance_id, user_id, ip_address, details) VALUES (%s, %s, %s, %s, %s)",
            ("EDIT", attendance_id, user_id, ip_address, f"new_status={new_status}")
        )
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()


def delete_attendance(
    conn, *, attendance_id: int, user_id: int, ip_address: str
) -> None:
    """Delete attendance record."""
    cur = conn.cursor()
    try:
        # Log before deletion since attendance_id will be gone
        cur.execute(
            "INSERT INTO audit_logs (action_type, attendance_id, user_id, ip_address, details) VALUES (%s, %s, %s, %s, %s)",
            ("DELETE", attendance_id, user_id, ip_address, "row deleted")
        )
        
        # Delete attendance record
        cur.execute("DELETE FROM attendance WHERE id = %s", (attendance_id,))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()


def attempt_modify_audit_logs(
    conn, *, operation: str, user_id: int, ip_address: str
) -> None:
    """Attempt to modify audit logs (for testing tamper detection)."""
    try:
        cur = conn.cursor()
        if operation.upper() == "UPDATE":
            cur.execute("UPDATE audit_logs SET details = 'tampered' WHERE id = -1")
        elif operation.upper() == "DELETE":
            cur.execute("DELETE FROM audit_logs WHERE id = -1")
        else:
            raise ValueError("Unsupported operation")
        conn.commit()
        cur.close()
    except mysql.connector.Error as e:
        log_security_event(
            conn,
            event_type=f"{operation.upper()}_ATTEMPT",
            user_id=user_id,
            ip_address=ip_address,
            target_table="audit_logs",
            operation=operation.upper(),
            details=str(e),
        )
        try:
            log_action(
                conn,
                action_type="LOG_MOD_ATTEMPT",
                attendance_id=None,
                user_id=user_id,
                ip_address=ip_address,
                details=f"{operation.upper()} blocked: {e}",
            )
        except Exception:
            pass
        raise
