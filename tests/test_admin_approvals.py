from datetime import datetime, timezone
import pytest
from src.app import submit_correction_request, review_request_by_faculty, override_request_by_admin, get_conn

def test_faculty_approve_updates_attendance_and_notifies(seed_basic, monkeypatch):
    s = seed_basic
    fake_now = datetime(2025, 11, 9, 8, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr("src.app._now_utc", lambda: fake_now)

    req_id = submit_correction_request(s["student_id"], s["course_id"], "2025-11-07T09:00:00+00:00", "present", "I was present")
    updated = review_request_by_faculty(s["faculty_id"], req_id, "approve")
    assert updated["status"] == "approved"

    with get_conn() as conn:
        att = conn.execute(
            "SELECT status FROM attendance WHERE student_id=? AND course_id=? AND session_dt=?",
            (s["student_id"], s["course_id"], "2025-11-07T09:00:00+00:00"),
        ).fetchone()
        assert att["status"] == "present"

        n = conn.execute("SELECT COUNT(*) c FROM notifications WHERE user_id=?", (s["student_id"],)).fetchone()["c"]
        assert n >= 2

def test_faculty_reject_requires_reason(seed_basic, monkeypatch):
    s = seed_basic
    fake_now = datetime(2025, 11, 9, 8, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr("src.app._now_utc", lambda: fake_now)

    req_id = submit_correction_request(s["student_id"], s["course_id"], "2025-11-07T09:00:00+00:00", "present", "reason")

    with pytest.raises(ValueError):
        review_request_by_faculty(s["faculty_id"], req_id, "reject", "")

def test_admin_override(seed_basic, monkeypatch):
    s = seed_basic
    fake_now = datetime(2025, 11, 9, 8, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr("src.app._now_utc", lambda: fake_now)

    req_id = submit_correction_request(s["student_id"], s["course_id"], "2025-11-07T09:00:00+00:00", "present", "reason")

    review_request_by_faculty(s["faculty_id"], req_id, "reject", "Insufficient proof")

    updated = override_request_by_admin(s["admin_id"], req_id, "approved", "Edge case validated")
    assert updated["status"] == "approved"

    with get_conn() as conn:
        att = conn.execute(
            "SELECT status FROM attendance WHERE student_id=? AND course_id=? AND session_dt=?",
            (s["student_id"], s["course_id"], "2025-11-07T09:00:00+00:00"),
        ).fetchone()
        assert att["status"] == "present"

        log = conn.execute("SELECT COUNT(*) c FROM audit_log").fetchone()["c"]
        assert log >= 3
