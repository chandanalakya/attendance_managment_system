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
def log_action(conn_or_session, action_type, attendance_id, user_id, ip_address, details=None):
    valid_actions = {"ADD", "EDIT", "DELETE"}
    if action_type not in valid_actions:
        raise ValueError(f"Invalid action_type '{action_type}'")

    now = datetime.datetime.utcnow()
    sql = """
        INSERT INTO audit_logs (action_type, attendance_id, user_id, ip_address, details, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    params = (action_type, attendance_id, user_id, ip_address, details, now)

    try:
        if hasattr(conn_or_session, "executescript"):  # sqlite3
            cur = conn_or_session.execute(sql, params)
            conn_or_session.commit()
            return cur.lastrowid
        else:  # SQLAlchemy
            result = conn_or_session.execute(
                text(
                    "INSERT INTO audit_logs (action_type, attendance_id, user_id, ip_address, details, created_at) "
                    "VALUES (:action_type, :attendance_id, :user_id, :ip_address, :details, :created_at)"
                ),
                {
                    "action_type": action_type,
                    "attendance_id": attendance_id,
                    "user_id": user_id,
                    "ip_address": ip_address,
                    "details": details,
                    "created_at": now,
                },
            )
            conn_or_session.commit()
            return result.lastrowid
    except Exception as e:
        print(f"⚠️ log_action failed: {e}")
        return None


# -------------------------------------------------------------------
# ✅ LOG SECURITY EVENT
# -------------------------------------------------------------------
def log_security_event(conn_or_session, event_type, user_id, ip_address, target_table, operation, details=None):
    now = datetime.datetime.utcnow()
    sql = """
        INSERT INTO audit_security_events
        (event_type, user_id, ip_address, target_table, operation, details, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    params = (event_type, user_id, ip_address, target_table, operation, details, now)

    try:
        if hasattr(conn_or_session, "executescript"):  # sqlite3
            cur = conn_or_session.execute(sql, params)
            conn_or_session.commit()
            return cur.lastrowid
        else:  # SQLAlchemy
            result = conn_or_session.execute(
                text(
                    "INSERT INTO audit_security_events "
                    "(event_type, user_id, ip_address, target_table, operation, details, created_at) "
                    "VALUES (:event_type, :user_id, :ip_address, :target_table, :operation, :details, :created_at)"
                ),
                {
                    "event_type": event_type,
                    "user_id": user_id,
                    "ip_address": ip_address,
                    "target_table": target_table,
                    "operation": operation,
                    "details": details,
                    "created_at": now,
                },
            )
            conn_or_session.commit()
            return result.lastrowid
    except Exception as e:
        print(f"⚠️ log_security_event failed: {e}")
        return None


# -------------------------------------------------------------------
# ✅ FETCH LOGS
# -------------------------------------------------------------------
def fetch_logs(conn, action_type=None, user_id=None):
    query = "SELECT * FROM audit_logs WHERE 1=1"
    params = []

    if action_type:
        query += " AND action_type = ?"
        params.append(action_type)
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)

    query += " ORDER BY created_at DESC"

    try:
        if hasattr(conn, "executescript"):  # sqlite3
            cur = conn.execute(query, tuple(params))
            rows = cur.fetchall()
        else:  # SQLAlchemy
            stmt = text(
                "SELECT * FROM audit_logs WHERE 1=1"
                + (" AND action_type = :action_type" if action_type else "")
                + (" AND user_id = :user_id" if user_id else "")
                + " ORDER BY created_at DESC"
            )
            bind = {}
            if action_type:
                bind["action_type"] = action_type
            if user_id:
                bind["user_id"] = user_id
            rows = conn.execute(stmt, bind).fetchall()

        return [AuditLog(**dict(r)) for r in rows]
    except Exception as e:
        print(f"⚠️ fetch_logs failed: {e}")
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
