import sqlite3
from .audit_log import log_action, log_security_event


def add_attendance(
    conn: sqlite3.Connection,
    *,
    course_id: int,
    student_id: int,
    status: str,
    taken_by_user_id: int,
    ip_address: str,
    notes: str = "",
) -> int:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO attendance (course_id, student_id, status, taken_by_user_id, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (course_id, student_id, status, taken_by_user_id, notes),
    )
    conn.commit()
    attendance_id = cur.lastrowid
    log_action(
        conn,
        action_type="ADD",
        attendance_id=attendance_id,
        user_id=taken_by_user_id,
        ip_address=ip_address,
        details=f"status={status}",
    )
    return attendance_id


def edit_attendance(
    conn: sqlite3.Connection,
    *,
    attendance_id: int,
    new_status: str,
    user_id: int,
    ip_address: str,
    notes: str = "",
) -> None:
    conn.execute(
        "UPDATE attendance SET status = ?, notes = ? WHERE id = ?",
        (new_status, notes, attendance_id),
    )
    conn.commit()
    log_action(
        conn,
        action_type="EDIT",
        attendance_id=attendance_id,
        user_id=user_id,
        ip_address=ip_address,
        details=f"new_status={new_status}",
    )


def delete_attendance(
    conn: sqlite3.Connection, *, attendance_id: int, user_id: int, ip_address: str
) -> None:
    conn.execute("DELETE FROM attendance WHERE id = ?", (attendance_id,))
    conn.commit()
    log_action(
        conn,
        action_type="DELETE",
        attendance_id=attendance_id,
        user_id=user_id,
        ip_address=ip_address,
        details="row deleted",
    )


def attempt_modify_audit_logs(
    conn: sqlite3.Connection, *, operation: str, user_id: int, ip_address: str
):
    try:
        if operation.upper() == "UPDATE":
            conn.execute("UPDATE audit_logs SET details = 'tampered' WHERE id = -1")
        elif operation.upper() == "DELETE":
            conn.execute("DELETE FROM audit_logs WHERE id = -1")
        else:
            raise ValueError("Unsupported op")
        conn.commit()
    except sqlite3.DatabaseError as e:
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
