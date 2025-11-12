from src.app import edit_attendance, get_conn

def test_faculty_can_edit_attendance(seed_basic):
    s = seed_basic
    att_id = edit_attendance(
        s["faculty_id"],
        s["student_id"],
        s["course_id"],
        "2025-11-07T09:00:00+00:00",
        "present",
    )
    assert att_id > 0
    with get_conn() as conn:
        row = conn.execute("SELECT status FROM attendance WHERE id=?", (att_id,)).fetchone()
        assert row["status"] == "present"
