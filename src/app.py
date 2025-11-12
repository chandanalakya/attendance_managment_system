from __future__ import annotations
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, List, Dict
import hashlib

DB_PATH = os.environ.get(
    "ATTENDANCE_DB",
    os.path.join(os.path.dirname(__file__), "..", "attendance.db")
)

ISO = "%Y-%m-%dT%H:%M:%S%z"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime(ISO)


def _parse_iso(s: str) -> datetime:
    try:
        if s.endswith("Z"):
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        return datetime.fromisoformat(s)
    except ValueError:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(schema_path: Optional[str] = None):
    if schema_path is None:
        schema_path = os.path.join(os.path.dirname(__file__), "..", "schema.sql")
    with get_conn() as conn, open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())


# ================= AUTH HELPERS =====================

def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def create_user(name: str, email: str, password: str, role: str) -> int:
    with get_conn() as conn:
        try:
            cur = conn.execute(
                "INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)",
                (name, email, _hash_password(password), role),
            )
            return cur.lastrowid
        except sqlite3.IntegrityError:
            # Email already exists: return existing id instead of crashing
            row = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
            if row:
                return row["id"]
            raise



def find_user_by_email(email: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        return dict(row) if row else None


def login_user(email: str, password: str) -> Optional[dict]:
    user = find_user_by_email(email)
    if not user:
        return None
    if user["password_hash"] != _hash_password(password):
        return None
    return user


# ================= COMMON HELPERS =====================

def notify(user_id: int, message: str, channel: str = "in-app"):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO notifications(user_id,channel,message,created_at) VALUES(?,?,?,?)",
            (user_id, channel, message, _iso(_now_utc())),
        )


def audit(actor_id: int, action: str, entity: str, entity_id: int, details: str = ""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO audit_log(actor_id,action,entity,entity_id,details,created_at) VALUES(?,?,?,?,?,?)",
            (actor_id, action, entity, entity_id, details, _iso(_now_utc())),
        )


# ================= STUDENT REQUEST FEATURE =====================

def submit_correction_request(
    student_id: int,
    course_id: int,
    session_dt_iso: str,
    requested_status: str,
    reason: str,
) -> int:

    if requested_status not in ("present", "absent"):
        raise ValueError("requested_status must be 'present' or 'absent'")
    if not reason.strip():
        raise ValueError("reason is mandatory")

    session_dt = _parse_iso(session_dt_iso)
    now = _now_utc()

    if now - session_dt > timedelta(days=3):
        raise PermissionError("Requests can only be submitted within 3 days of the class session")

    with get_conn() as conn:
        att = conn.execute(
            "SELECT id,status FROM attendance WHERE student_id=? AND course_id=? AND session_dt=?",
            (student_id, course_id, session_dt_iso),
        ).fetchone()
        if att is None:
            raise LookupError("Attendance record not found for that session")

        existing = conn.execute(
            """
            SELECT id FROM attendance_corrections
            WHERE student_id=? AND course_id=? AND session_dt=?
            """,
            (student_id, course_id, session_dt_iso),
        ).fetchone()
        if existing:
            raise FileExistsError("Duplicate request for the same date/class is not allowed")

        cur = conn.execute(
            """
            INSERT INTO attendance_corrections
            (student_id,course_id,session_dt,requested_status,reason,status,created_at,updated_at)
            VALUES(?,?,?,?,?,'pending',?,?)
            """,
            (
                student_id,
                course_id,
                session_dt_iso,
                requested_status,
                reason.strip(),
                _iso(now),
                _iso(now),
            ),
        )
        req_id = cur.lastrowid

    audit(student_id, "request_submitted", "attendance_correction", req_id, f"Requested {requested_status}")
    notify(student_id, "Your attendance correction request has been submitted for review.")
    return req_id


# ================= FACULTY REVIEW FEATURE =====================

def review_request_by_faculty(
    faculty_id: int,
    request_id: int,
    decision: str,
    comment: Optional[str] = None,
) -> dict:

    if decision not in ("approve", "reject"):
        raise ValueError("decision must be 'approve' or 'reject'")
    if decision == "reject" and not comment.strip():
        raise ValueError("Rejection requires a mandatory reason")

    with get_conn() as conn:
        req = conn.execute("SELECT * FROM attendance_corrections WHERE id=?", (request_id,)).fetchone()
        if req is None:
            raise LookupError("Correction request not found")

        if req["status"] != "pending":
            raise PermissionError("Only pending requests can be updated")

        if decision == "approve":
            new_status = "approved"
            conn.execute(
                "UPDATE attendance SET status=? WHERE student_id=? AND course_id=? AND session_dt=?",
                (req["requested_status"], req["student_id"], req["course_id"], req["session_dt"]),
            )
        else:
            new_status = "rejected"

        conn.execute(
            """
            UPDATE attendance_corrections
            SET status=?, faculty_reviewer_id=?, faculty_comment=?, updated_at=?
            WHERE id=?
            """,
            (
                new_status,
                faculty_id,
                (comment or "").strip(),
                _iso(_now_utc()),
                request_id,
            ),
        )
        updated = conn.execute("SELECT * FROM attendance_corrections WHERE id=?", (request_id,)).fetchone()

    if decision == "approve":
        audit(faculty_id, "faculty_approved", "attendance_correction", request_id, (comment or ""))
        notify(updated["student_id"], "Your attendance correction request has been APPROVED.")
    else:
        audit(faculty_id, "faculty_rejected", "attendance_correction", request_id, comment or "")
        notify(updated["student_id"], "Your attendance correction request has been REJECTED.")

    return dict(updated)


# ================= ADMIN OVERRIDE FEATURE =====================

def override_request_by_admin(
    admin_id: int,
    request_id: int,
    override_status: str,
    justification: str,
) -> dict:

    if override_status not in ("approved", "rejected", "pending"):
        raise ValueError("override_status must be 'approved', 'rejected', or 'pending'")
    if not justification.strip():
        raise ValueError("Admin override requires a justification")

    with get_conn() as conn:
        req = conn.execute("SELECT * FROM attendance_corrections WHERE id=?", (request_id,)).fetchone()
        if req is None:
            raise LookupError("Correction request not found")

        if override_status == "approved":
            conn.execute(
                "UPDATE attendance SET status=? WHERE student_id=? AND course_id=? AND session_dt=?",
                (req["requested_status"], req["student_id"], req["course_id"], req["session_dt"]),
            )

        conn.execute(
            """
            UPDATE attendance_corrections
            SET status=?, admin_reviewer_id=?, admin_comment=?, updated_at=?
            WHERE id=?
            """,
            (
                override_status,
                admin_id,
                justification.strip(),
                _iso(_now_utc()),
                request_id,
            ),
        )
        updated = conn.execute("SELECT * FROM attendance_corrections WHERE id=?", (request_id,)).fetchone()

    audit(admin_id, "admin_override", "attendance_correction", request_id, justification)
    notify(updated["student_id"], "An admin has overridden a decision on your attendance request.")
    return dict(updated)


# ================= FAKE FACULTY DIRECT EDIT FEATURE (used in tests) =====================

def edit_attendance(faculty_id: int, student_id: int, course_id: int, session_dt_iso: str, new_status: str) -> int:
    if new_status not in ("present", "absent"):
        raise ValueError("new_status must be 'present' or 'absent'")

    with get_conn() as conn:
        att = conn.execute(
            "SELECT id FROM attendance WHERE student_id=? AND course_id=? AND session_dt=?",
            (student_id, course_id, session_dt_iso),
        ).fetchone()
        if att is None:
            cur = conn.execute(
                "INSERT INTO attendance(student_id, course_id, session_dt, status) VALUES(?,?,?,?)",
                (student_id, course_id, session_dt_iso, new_status),
            )
            att_id = cur.lastrowid
        else:
            conn.execute("UPDATE attendance SET status=? WHERE id=?", (new_status, att["id"]))
            att_id = att["id"]

    audit(faculty_id, "faculty_edit", "attendance", att_id, f"Set {new_status}")
    return att_id


# alias used by legacy tests
def approve_edit_request(*args, **kwargs):
    return review_request_by_faculty(*args, decision="approve", **kwargs)
