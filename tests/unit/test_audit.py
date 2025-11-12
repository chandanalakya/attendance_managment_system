import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from src.utils.db import init_db, get_conn

# Try importing audit_log; skip tests if not available
try:
    from src.models.audit_log import log_action, log_security_event, fetch_logs
    AUDIT_AVAILABLE = True
except ImportError:
    AUDIT_AVAILABLE = False

SCHEMA = "src/schema.sql"

@pytest.mark.skipif(not AUDIT_AVAILABLE, reason="audit_log module not available")
def test_log_action_creates_entry(tmp_path):
    init_db(SCHEMA)
    with get_conn() as conn:
        conn.execute("INSERT INTO users (username, role) VALUES ('admin', 'admin')")
        conn.commit()
        log_id = log_action(conn, action_type="ADD", attendance_id=None, user_id=1, ip_address="127.0.0.1", details="Added record")
        result = conn.execute("SELECT * FROM audit_logs WHERE id=?", (log_id,)).fetchone()
        assert result is not None
        assert result["action_type"] == "ADD"
        assert result["ip_address"] == "127.0.0.1"

@pytest.mark.skipif(not AUDIT_AVAILABLE, reason="audit_log module not available")
def test_invalid_action_type_raises(tmp_path):
    init_db(SCHEMA)
    with get_conn() as conn:
        conn.execute("INSERT INTO users (username, role) VALUES ('user','admin')")
        conn.commit()
        with pytest.raises(ValueError):
            log_action(conn, action_type="FAKE_ACTION", attendance_id=1, user_id=1, ip_address="127.0.0.1")

@pytest.mark.skipif(not AUDIT_AVAILABLE, reason="audit_log module not available")
def test_fetch_logs_filters_correctly(tmp_path):
    init_db(SCHEMA)
    with get_conn() as conn:
        conn.execute("INSERT INTO users (username, role) VALUES ('user','admin')")
        conn.commit()
        log_action(conn, action_type="ADD", attendance_id=None, user_id=1, ip_address="1.1.1.1", details="First log")
        log_action(conn, action_type="EDIT", attendance_id=None, user_id=1, ip_address="1.1.1.1", details="Second log")
        rows = fetch_logs(conn, user_id=1)
        assert len(rows) == 2
        assert {r['action_type'] for r in rows} == {"ADD", "EDIT"}

@pytest.mark.skipif(not AUDIT_AVAILABLE, reason="audit_log module not available")
def test_log_security_event_creates_entry(tmp_path):
    init_db(SCHEMA)
    with get_conn() as conn:
        conn.execute("INSERT INTO users (username, role) VALUES ('admin','admin')")
        conn.commit()
        event_id = log_security_event(conn, event_type="UPDATE_ATTEMPT", user_id=1, ip_address="10.0.0.1", target_table="audit_logs", operation="UPDATE", details="Blocked update")
        event = conn.execute("SELECT * FROM audit_security_events WHERE id=?", (event_id,)).fetchone()
        assert event["event_type"] == "UPDATE_ATTEMPT"
        assert event["target_table"] == "audit_logs"
