import pytest
from datetime import datetime, timezone
from src.app import submit_correction_request, get_conn

def test_student_can_submit_request_with_rules(seed_basic, monkeypatch):
    s = seed_basic
    fake_now = datetime(2025, 11, 9, 8, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr("src.app._now_utc", lambda: fake_now)

    req_id = submit_correction_request(
        student_id=s["student_id"],
        course_id=s["course_id"],
        session_dt_iso="2025-11-07T09:00:00+00:00",
        requested_status="present",
        reason="I was present; swipe failed",
    )
    assert req_id > 0

    with get_conn() as conn:
        row = conn.execute("SELECT * FROM attendance_corrections WHERE id=?", (req_id,)).fetchone()
        assert row["status"] == "pending"

def test_duplicate_and_window_rules(seed_basic, monkeypatch):
    s = seed_basic
    fake_now = datetime(2025, 11, 10, 9, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr("src.app._now_utc", lambda: fake_now)

    submit_correction_request(s["student_id"], s["course_id"], "2025-11-07T09:00:00+00:00", "present", "valid")

    with pytest.raises(FileExistsError):
        submit_correction_request(s["student_id"], s["course_id"], "2025-11-07T09:00:00+00:00", "present", "dup")

    far_now = datetime(2025, 11, 11, 15, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr("src.app._now_utc", lambda: far_now)

    with pytest.raises(PermissionError):
        submit_correction_request(s["student_id"], s["course_id"], "2025-11-07T09:00:00+00:00", "present", "late")
