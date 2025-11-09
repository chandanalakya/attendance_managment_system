
from typing import Optional, List, Dict, Any
import sqlite3

ALLOWED_ACTIONS = {"ADD","EDIT","DELETE","LOG_MOD_ATTEMPT"}

def log_action(conn: sqlite3.Connection, *, action_type: str, attendance_id: Optional[int], user_id: int, ip_address: str, details: str = "") -> int:
    if action_type not in ALLOWED_ACTIONS:
        raise ValueError("Invalid action type")
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO audit_logs (action_type, attendance_id, user_id, ip_address, details)
        VALUES (?, ?, ?, ?, ?)
        """,
        (action_type, attendance_id, user_id, ip_address, details),
    )
    conn.commit()
    return cur.lastrowid

def log_security_event(conn: sqlite3.Connection, *, event_type: str, user_id: Optional[int], ip_address: str, target_table: str, operation: str, details: str = "") -> int:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO audit_security_events (event_type, user_id, ip_address, target_table, operation, details)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (event_type, user_id, ip_address, target_table, operation, details),
    )
    conn.commit()
    return cur.lastrowid

def fetch_logs(conn: sqlite3.Connection, *, start: Optional[str] = None, end: Optional[str] = None, user_id: Optional[int] = None, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
    q = """
        SELECT al.id, al.action_type, al.attendance_id, al.user_id, al.ip_address, al.details, al.created_at,
               a.course_id
        FROM audit_logs al
        LEFT JOIN attendance a ON a.id = al.attendance_id
        WHERE 1=1
    """
    params = []
    if start:
        q += " AND datetime(al.created_at) >= datetime(?)"
        params.append(start)
    if end:
        q += " AND datetime(al.created_at) <= datetime(?)"
        params.append(end)
    if user_id:
        q += " AND al.user_id = ?"
        params.append(user_id)
    if course_id:
        q += " AND a.course_id = ?"
        params.append(course_id)
    q += " ORDER BY al.created_at DESC, al.id DESC"
    rows = conn.execute(q, params).fetchall()
    return [dict(r) for r in rows]
