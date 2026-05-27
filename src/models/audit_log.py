import datetime
from sqlalchemy import text

# -------------------------------------------------------------------
# ✅ AuditLog Model
# -------------------------------------------------------------------
class AuditLog:
    def __init__(self, id, action_type, attendance_id, user_id, ip_address, details, created_at):
        self.id = id
        self.action_type = action_type
        self.attendance_id = attendance_id
        self.user_id = user_id
        self.ip_address = ip_address
        self.details = details
        self.created_at = created_at

    def to_dict(self):
        return {
            "id": self.id,
            "action_type": self.action_type,
            "attendance_id": self.attendance_id,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "details": self.details,
            "created_at": self.created_at,
        }

    def __getitem__(self, key):
        return getattr(self, key)


# -------------------------------------------------------------------
# ✅ LOG ACTION
# -------------------------------------------------------------------
def log_action(conn, action_type, attendance_id, user_id, ip_address, details=None):
    """Log an action to audit_logs table."""
    valid_actions = {"ADD", "EDIT", "DELETE", "LOG_MOD_ATTEMPT"}
    if action_type not in valid_actions:
        raise ValueError(f"Invalid action_type '{action_type}'")

    try:
        cursor = conn.cursor()
        # For DELETE actions or when attendance_id doesn't exist, set to NULL
        if action_type == "DELETE" or attendance_id is None:
            attendance_id = None
        else:
            # Verify attendance_id exists before logging
            cursor.execute("SELECT id FROM attendance WHERE id = %s", (attendance_id,))
            if not cursor.fetchone():
                attendance_id = None
        
        cursor.execute(
            "INSERT INTO audit_logs (action_type, attendance_id, user_id, ip_address, details) VALUES (%s, %s, %s, %s, %s)",
            (action_type, attendance_id, user_id, ip_address, details)
        )
        conn.commit()
        log_id = cursor.lastrowid
        cursor.close()
        return log_id
    except Exception as e:
        print(f"log_action failed: {e}")
        return None


# -------------------------------------------------------------------
# ✅ LOG SECURITY EVENT
# -------------------------------------------------------------------
def log_security_event(conn, event_type, user_id, ip_address, target_table, operation, details=None):
    """Log a security event to audit_security_events table."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_security_events (event_type, user_id, ip_address, target_table, operation, details) VALUES (%s, %s, %s, %s, %s, %s)",
            (event_type, user_id, ip_address, target_table, operation, details)
        )
        conn.commit()
        event_id = cursor.lastrowid
        cursor.close()
        return event_id
    except Exception as e:
        print(f"log_security_event failed: {e}")
        return None


# -------------------------------------------------------------------
# ✅ FETCH LOGS
# -------------------------------------------------------------------
def fetch_logs(conn, start=None, end=None, user_id=None, course_id=None):
    """Fetch audit logs with optional filters."""
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []

        if start:
            query += " AND created_at >= %s"
            params.append(start)
        if end:
            query += " AND created_at <= %s"
            params.append(end)
        if user_id:
            query += " AND user_id = %s"
            params.append(user_id)
        if course_id:
            query += " AND attendance_id IN (SELECT id FROM attendance WHERE course_id = %s)"
            params.append(course_id)

        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        
        # Convert to dict format
        columns = ['id', 'action_type', 'attendance_id', 'user_id', 'ip_address', 'details', 'created_at']
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"fetch_logs failed: {e}")
        return []


# -------------------------------------------------------------------
# ✅ ATTEMPT TO MODIFY AUDIT LOGS (TAMPER DETECTION)
# -------------------------------------------------------------------
def attempt_modify_audit_logs(conn, operation, user_id, ip_address):
    """
    Simulates a tampering attempt on audit_logs.
    Always logs a security event regardless of update success or failure.
    Guarantees visibility of the audit_security_events entry.
    """
    tamper_detected = False

    try:
        # Try to tamper with audit_logs (will fail due to immutability trigger)
        conn.execute("UPDATE audit_logs SET details='tampered' WHERE id=1")
        conn.commit()
        tamper_detected = True
    except Exception as e:
        print(f"⚠️ Tamper update blocked ({type(e).__name__}): {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        tamper_detected = True  # Even failure is a tamper attempt

    # ✅ Explicitly ensure event is logged no matter what
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO audit_security_events (
                event_type, user_id, ip_address, target_table, operation, details, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                "UPDATE_ATTEMPT",
                user_id,
                ip_address,
                "audit_logs",
                operation,
                "Tampering attempt detected" if tamper_detected else "Unexpected state",
            ),
        )
        conn.commit()

        # Debug confirmation
        count = conn.execute("SELECT COUNT(*) FROM audit_security_events").fetchone()[0]
        print(f"✅ Security event inserted. Total events now: {count}")
    except Exception as e:
        print(f"⚠️ Failed to insert audit_security_event: {e}")
        conn.rollback()
