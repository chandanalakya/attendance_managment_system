import streamlit as st
import mysql.connector
import bcrypt
import os
import pathlib
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta, timezone

# ===================================================
# ENV & APP SETUP
# ===================================================
env_path = pathlib.Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "sams_db")

st.set_page_config(page_title="SAMS — Attendance Management", layout="wide")

# ---------------------------------------------------
# Session initialization
# ---------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# ===================================================
# DB CONNECTION
# ===================================================
def get_db_conn():
    return mysql.connector.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASS,
        database=DB_NAME, auth_plugin="mysql_native_password"
    )

# ===================================================
# BASE SCHEMA (USERS & DETAILS ARE ASSUMED TO EXIST)
# + ATTENDANCE + EDIT/AUDIT + NOTIFICATIONS
# ===================================================
BASE_SCHEMA = """
CREATE TABLE IF NOT EXISTS attendance_sessions (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  faculty_id BIGINT NOT NULL,
  course VARCHAR(100),
  session_date DATETIME NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX (faculty_id),
  CONSTRAINT fk_att_sess_user FOREIGN KEY (faculty_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS attendance_records (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  session_id BIGINT NOT NULL,
  student_id BIGINT NOT NULL,
  status ENUM('Present','Absent') NOT NULL,
  last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uniq_session_student (session_id, student_id),
  INDEX (student_id),
  CONSTRAINT fk_att_rec_session FOREIGN KEY (session_id) REFERENCES attendance_sessions(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_att_rec_student FOREIGN KEY (student_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS attendance_edit_requests (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  record_id BIGINT NOT NULL,
  session_id BIGINT NOT NULL,
  student_id BIGINT NOT NULL,
  old_status ENUM('Present','Absent') NOT NULL,
  new_status ENUM('Present','Absent') NOT NULL,
  justification TEXT NOT NULL,
  requested_by_faculty_id BIGINT NULL,
  requested_by_faculty_name VARCHAR(255),
  status ENUM('PENDING','APPROVED','REJECTED') DEFAULT 'PENDING', -- ADMIN FINAL
  requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  reviewed_by_admin_id BIGINT NULL,
  reviewed_at DATETIME NULL,
  admin_note TEXT NULL,
  CONSTRAINT fk_edit_req_record FOREIGN KEY (record_id) REFERENCES attendance_records(id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS attendance_edit_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  record_id BIGINT NOT NULL,
  session_id BIGINT NOT NULL,
  student_id BIGINT NOT NULL,
  old_status ENUM('Present','Absent') NOT NULL,
  new_status ENUM('Present','Absent') NOT NULL,
  edited_by_faculty_id BIGINT NOT NULL,
  edited_by_faculty_name VARCHAR(255),
  justification TEXT NOT NULL,
  edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  approval_required TINYINT(1) NOT NULL DEFAULT 0,
  edit_request_id BIGINT NULL,
  approved_by_admin_id BIGINT NULL,
  approved_at DATETIME NULL,
  admin_note TEXT NULL,
  INDEX (record_id),
  CONSTRAINT fk_audit_record FOREIGN KEY (record_id) REFERENCES attendance_records(id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- In-app notifications
CREATE TABLE IF NOT EXISTS notifications (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  message TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  read_at DATETIME NULL,
  INDEX (user_id),
  CONSTRAINT fk_notif_user FOREIGN KEY (user_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

# Patches to reuse attendance_edit_requests for STUDENT-initiated flow & FACULTY review
SCHEMA_PATCHES = [
    """
    ALTER TABLE attendance_edit_requests
    ADD COLUMN IF NOT EXISTS requested_by_role ENUM('FACULTY','STUDENT') DEFAULT 'FACULTY',
    ADD COLUMN IF NOT EXISTS requested_by_student_id BIGINT NULL,
    ADD COLUMN IF NOT EXISTS faculty_status ENUM('PENDING','APPROVED','REJECTED') DEFAULT 'PENDING',
    ADD COLUMN IF NOT EXISTS reviewed_by_faculty_id BIGINT NULL,
    ADD COLUMN IF NOT EXISTS faculty_decision_note TEXT NULL,
    ADD COLUMN IF NOT EXISTS faculty_decided_at DATETIME NULL;
    """,
    """
    ALTER TABLE attendance_edit_log
    ADD COLUMN IF NOT EXISTS faculty_reviewer_id BIGINT NULL,
    ADD COLUMN IF NOT EXISTS faculty_reviewed_at DATETIME NULL,
    ADD COLUMN IF NOT EXISTS faculty_note TEXT NULL,
    ADD COLUMN IF NOT EXISTS faculty_decision ENUM('APPROVED','REJECTED') NULL;
    """
]

def init_schema():
    conn = get_db_conn()
    cur = conn.cursor()
    for stmt in [s.strip() for s in BASE_SCHEMA.split(";") if s.strip()]:
        cur.execute(stmt)
    for patch in SCHEMA_PATCHES:
        for stmt in [s.strip() for s in patch.split(";") if s.strip()]:
            try:
                cur.execute(stmt)
            except mysql.connector.Error:
                # Best-effort for IF NOT EXISTS on older MySQL
                pass
    conn.commit()
    cur.close(); conn.close()

init_schema()

# ===================================================
# HELPER FUNCTIONS (USERS, DETAILS)
# ===================================================
def find_user_by_email(email):
    conn = get_db_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def create_user(email, password, role="student", approved=False):
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (email, password_hash, role, is_approved) VALUES (%s,%s,%s,%s)",
        (email, pw_hash, role, approved)
    )
    conn.commit()
    cur.close()
    conn.close()

def approve_user(user_id):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_approved=TRUE WHERE id=%s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def reject_user(user_id):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def get_student_details(user_id):
    conn = get_db_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM student_details WHERE user_id=%s", (user_id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data

def save_student_details(user_id, full_name, roll_no, department, course, semester, section):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO student_details (user_id, full_name, roll_no, department, course, semester, section)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
        full_name=VALUES(full_name), roll_no=VALUES(roll_no),
        department=VALUES(department), course=VALUES(course),
        semester=VALUES(semester), section=VALUES(section);
    """, (user_id, full_name, roll_no, department, course, semester, section))
    conn.commit()
    cur.close()
    conn.close()

def get_faculty_details(user_id):
    conn = get_db_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM faculty_details WHERE user_id=%s", (user_id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data

def save_faculty_details(user_id, full_name, faculty_id, department, course, designation):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO faculty_details (user_id, full_name, faculty_id, department, course, designation)
        VALUES (%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
        full_name=VALUES(full_name), faculty_id=VALUES(faculty_id),
        department=VALUES(department), course=VALUES(course),
        designation=VALUES(designation);
    """, (user_id, full_name, faculty_id, department, course, designation))
    conn.commit()
    cur.close()
    conn.close()

def verify_password(pw, pw_hash):
    return bcrypt.checkpw(pw.encode(), pw_hash.encode())

def login_user(email, password):
    user = find_user_by_email(email)
    if not user:
        return False, "No such user."
    if not user["is_approved"]:
        return False, "Account pending admin approval."
    if verify_password(password, user["password_hash"]):
        return True, user
    return False, "Invalid password."

# ===================================================
# ATTENDANCE BACKEND (FACULTY EDIT WORKFLOW)
# ===================================================
def _get_faculty_name(faculty_user_id: int) -> str:
    conn = get_db_conn(); cur = conn.cursor()
    cur.execute("SELECT full_name FROM faculty_details WHERE user_id=%s", (faculty_user_id,))
    r = cur.fetchone()
    if r and r[0]:
        cur.close(); conn.close(); return r[0]
    cur.execute("SELECT email FROM users WHERE id=%s", (faculty_user_id,))
    r = cur.fetchone(); cur.close(); conn.close()
    return r[0] if r else f"User#{faculty_user_id}"

def _get_admin_name(admin_user_id: int) -> str:
    conn = get_db_conn(); cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE id=%s AND role='admin'", (admin_user_id,))
    r = cur.fetchone(); cur.close(); conn.close()
    return r[0] if r else f"Admin#{admin_user_id}"

def _validate_status(v: str):
    if v not in ("Present","Absent"):
        raise ValueError("status must be 'Present' or 'Absent'.")

def get_past_sessions(faculty_id: int, limit: int = 200):
    conn = get_db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id, session_date, course, created_at
        FROM attendance_sessions
        WHERE faculty_id=%s
        ORDER BY session_date DESC
        LIMIT %s
    """, (faculty_id, limit))
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows

def get_session_records(session_id: int):
    conn = get_db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT r.id AS record_id, r.student_id, r.status, r.last_modified_at,
               u.email AS student_email, sd.full_name AS student_name, sd.roll_no
        FROM attendance_records r
        JOIN users u ON u.id = r.student_id
        LEFT JOIN student_details sd ON sd.user_id = r.student_id
        WHERE r.session_id=%s
        ORDER BY sd.roll_no IS NULL, sd.roll_no, sd.full_name
    """, (session_id,))
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows

def edit_attendance(record_id: int, new_status: str, justification: str, faculty_id: int):
    _validate_status(new_status)
    if not justification or len(justification.strip()) < 10:
        raise ValueError("Justification must be at least 10 characters.")
    conn = get_db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT r.id AS record_id, r.session_id, r.student_id, r.status AS old_status,
               s.session_date, s.faculty_id AS owner_faculty_id
        FROM attendance_records r
        JOIN attendance_sessions s ON s.id = r.session_id
        WHERE r.id=%s FOR UPDATE
    """, (record_id,))
    rec = cur.fetchone()
    if not rec:
        cur.close(); conn.close(); raise ValueError("Record not found.")
    if rec["owner_faculty_id"] != faculty_id:
        cur.close(); conn.close(); raise PermissionError("You do not own this session.")
    if rec["old_status"] == new_status:
        cur.close(); conn.close()
        return {"applied": False, "message":"No change."}
    faculty_name = _get_faculty_name(faculty_id)
    session_age_hours = (datetime.utcnow() - rec["session_date"]).total_seconds()/3600.0
    applied_immediately = session_age_hours <= 24.0
    try:
        if applied_immediately:
            c = conn.cursor()
            c.execute("UPDATE attendance_records SET status=%s WHERE id=%s", (new_status, record_id))
            c.execute("""
                INSERT INTO attendance_edit_log
                (record_id, session_id, student_id, old_status, new_status,
                 edited_by_faculty_id, edited_by_faculty_name, justification, approval_required)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,0)
            """, (rec["record_id"], rec["session_id"], rec["student_id"], rec["old_status"],
                  new_status, faculty_id, faculty_name, justification))
            conn.commit(); c.close(); cur.close(); conn.close()
            return {"applied": True, "approval_required": False, "message":"Updated."}
        else:
            c = conn.cursor()
            c.execute("""
                INSERT INTO attendance_edit_requests
                (record_id, session_id, student_id, old_status, new_status, justification,
                 requested_by_faculty_id, requested_by_faculty_name, requested_by_role, requested_by_student_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'FACULTY',NULL)
            """, (rec["record_id"], rec["session_id"], rec["student_id"], rec["old_status"],
                  new_status, justification, faculty_id, faculty_name))
            request_id = c.lastrowid
            c.execute("""
                INSERT INTO attendance_edit_log
                (record_id, session_id, student_id, old_status, new_status,
                 edited_by_faculty_id, edited_by_faculty_name, justification,
                 approval_required, edit_request_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,1,%s)
            """, (rec["record_id"], rec["session_id"], rec["student_id"], rec["old_status"], new_status,
                  faculty_id, faculty_name, justification, request_id))
            conn.commit(); c.close(); cur.close(); conn.close()
            return {"applied": False, "approval_required": True, "request_id": request_id,
                    "message":"Queued for admin approval (>24h)."}
    except Exception:
        conn.rollback(); cur.close(); conn.close(); raise

def get_pending_edit_requests(limit: int = 200):
    conn = get_db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT r.id AS request_id, r.record_id, r.session_id, r.student_id,
               r.old_status, r.new_status, r.justification, r.requested_by_faculty_id,
               r.requested_by_faculty_name, r.status, r.requested_at,
               sd.full_name AS student_name, sd.roll_no, u.email AS student_email
        FROM attendance_edit_requests r
        JOIN users u ON u.id = r.student_id
        LEFT JOIN student_details sd ON sd.user_id = r.student_id
        WHERE r.requested_by_role='FACULTY' AND r.status='PENDING'
        ORDER BY r.requested_at ASC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows

def approve_edit_request(request_id: int, admin_id: int, approve: bool, admin_note: str | None = None):
    conn = get_db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM attendance_edit_requests WHERE id=%s FOR UPDATE", (request_id,))
    req = cur.fetchone()
    if not req:
        cur.close(); conn.close(); raise ValueError("Edit request not found.")
    if req["status"] != "PENDING":
        cur.close(); conn.close()
        return {"updated": False, "message": f"Already {req['status']}"}
    now = datetime.utcnow()
    try:
        c = conn.cursor()
        if approve:
            c.execute("UPDATE attendance_records SET status=%s WHERE id=%s", (req["new_status"], req["record_id"]))
            c.execute("""
                UPDATE attendance_edit_requests
                SET status='APPROVED', reviewed_by_admin_id=%s, reviewed_at=%s, admin_note=%s
                WHERE id=%s
            """, (admin_id, now, admin_note, request_id))
            c.execute("""
                UPDATE attendance_edit_log
                SET approved_by_admin_id=%s, approved_at=%s, admin_note=%s
                WHERE edit_request_id=%s
            """, (admin_id, now, admin_note, request_id))
        else:
            c.execute("""
                UPDATE attendance_edit_requests
                SET status='REJECTED', reviewed_by_admin_id=%s, reviewed_at=%s, admin_note=%s
                WHERE id=%s
            """, (admin_id, now, admin_note, request_id))
            c.execute("""
                UPDATE attendance_edit_log
                SET approved_by_admin_id=%s, approved_at=%s, admin_note=%s
                WHERE edit_request_id=%s
            """, (admin_id, now, admin_note, request_id))
        conn.commit(); c.close(); cur.close(); conn.close()
        return {"updated": True, "approved": approve, "message": "Decision saved."}
    except Exception:
        conn.rollback(); cur.close(); conn.close(); raise

# ===================================================
# STUDENT CORRECTION REQUESTS BACKEND
# (Reuses attendance_edit_requests with extra columns)
# ===================================================
def _get_student_name(uid: int)->str:
    conn = get_db_conn(); cur = conn.cursor()
    cur.execute("SELECT full_name FROM student_details WHERE user_id=%s", (uid,))
    r = cur.fetchone()
    if r and r[0]:
        cur.close(); conn.close(); return r[0]
    cur.execute("SELECT email FROM users WHERE id=%s",(uid,))
    r = cur.fetchone(); cur.close(); conn.close()
    return r[0] if r else f"Student#{uid}"

def _create_notification(user_id: int, message: str):
    conn = get_db_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO notifications (user_id, message) VALUES (%s,%s)", (user_id, message))
    conn.commit(); cur.close(); conn.close()

def _get_session_by_id(session_id: int):
    conn = get_db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT s.*, uf.email AS faculty_email, fd.full_name AS faculty_name
        FROM attendance_sessions s
        JOIN users uf ON uf.id = s.faculty_id
        LEFT JOIN faculty_details fd ON fd.user_id = s.faculty_id
        WHERE s.id=%s
    """, (session_id,))
    row = cur.fetchone(); cur.close(); conn.close()
    return row

def _get_record(session_id: int, student_id: int):
    conn = get_db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT r.*, sd.full_name AS student_name, u.email AS student_email
        FROM attendance_records r
        JOIN users u ON u.id = r.student_id
        LEFT JOIN student_details sd ON sd.user_id = r.student_id
        WHERE r.session_id=%s AND r.student_id=%s
    """, (session_id, student_id))
    row = cur.fetchone(); cur.close(); conn.close()
    return row

def submit_correction_request(student_id: int, session_id: int, new_status: str, justification: str):
    if new_status not in ("Present","Absent"):
        raise ValueError("new_status must be 'Present' or 'Absent'")
    if not justification or len(justification.strip()) < 10:
        raise ValueError("Reason must be at least 10 characters.")
    session = _get_session_by_id(session_id)
    if not session:
        raise ValueError("Session not found.")
    record = _get_record(session_id, student_id)
    if not record:
        raise PermissionError("You have no attendance record for this session.")
    if record["status"] == new_status:
        return {"created": False, "message":"No change: already that status."}
    # 3-day window
    if (datetime.utcnow() - session["session_date"]).total_seconds() > 3*24*3600:
        raise PermissionError("Requests allowed only within 3 days of session.")
    # Duplicate pending
    conn = get_db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id FROM attendance_edit_requests
        WHERE session_id=%s AND student_id=%s
          AND requested_by_role='STUDENT' AND status='PENDING'
    """, (session_id, student_id))
    if cur.fetchone():
        cur.close(); conn.close()
        raise ValueError("A pending request for this class already exists.")
    student_name = _get_student_name(student_id)
    c = conn.cursor()
    c.execute("""
        INSERT INTO attendance_edit_requests
        (record_id, session_id, student_id, old_status, new_status, justification,
         requested_by_role, requested_by_student_id, requested_by_faculty_id, requested_by_faculty_name,
         status, faculty_status)
        VALUES (%s,%s,%s,%s,%s,%s,'STUDENT',%s,NULL,NULL,'PENDING','PENDING')
    """, (record["id"], session_id, student_id, record["status"], new_status, justification, student_id))
    request_id = c.lastrowid
    c.execute("""
        INSERT INTO attendance_edit_log
        (record_id, session_id, student_id, old_status, new_status,
         edited_by_faculty_id, edited_by_faculty_name, justification,
         approval_required, edit_request_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,1,%s)
    """, (record["id"], session_id, student_id, record["status"], new_status, 0, f"Student:{student_name}", justification, request_id))
    conn.commit(); c.close(); cur.close(); conn.close()
    _create_notification(student_id, "Your attendance correction request has been submitted for review.")
    return {"created": True, "request_id": request_id, "message":"Request submitted."}

def get_student_correction_requests(student_id: int, limit: int = 200):
    conn = get_db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT r.id AS request_id, r.session_id, r.old_status, r.new_status,
               r.status AS admin_status, r.faculty_status,
               r.justification, r.requested_at, r.faculty_decision_note,
               s.session_date, s.course
        FROM attendance_edit_requests r
        JOIN attendance_sessions s ON s.id = r.session_id
        WHERE r.requested_by_role='STUDENT' AND r.student_id=%s
        ORDER BY r.requested_at DESC LIMIT %s
    """, (student_id, limit))
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows

def get_faculty_pending_requests(faculty_id: int, limit: int = 200):
    conn = get_db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT r.id AS request_id, r.record_id, r.session_id, r.student_id,
               r.old_status, r.new_status, r.justification, r.requested_at,
               sd.full_name AS student_name, u.email AS student_email,
               s.course, s.session_date
        FROM attendance_edit_requests r
        JOIN attendance_sessions s ON s.id = r.session_id
        JOIN users u ON u.id = r.student_id
        LEFT JOIN student_details sd ON sd.user_id = r.student_id
        WHERE s.faculty_id=%s
          AND r.requested_by_role='STUDENT'
          AND r.faculty_status='PENDING'
        ORDER BY r.requested_at ASC LIMIT %s
    """, (faculty_id, limit))
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows

def review_request_by_faculty(request_id: int, faculty_id: int, approve: bool, comment: str | None = None):
    conn = get_db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT r.*, s.faculty_id AS owner_faculty_id
        FROM attendance_edit_requests r
        JOIN attendance_sessions s ON s.id = r.session_id
        WHERE r.id=%s FOR UPDATE
    """, (request_id,))
    req = cur.fetchone()
    if not req:
        cur.close(); conn.close(); raise ValueError("Request not found.")
    if req["owner_faculty_id"] != faculty_id:
        cur.close(); conn.close(); raise PermissionError("You do not own this session.")
    if req["requested_by_role"] != "STUDENT":
        cur.close(); conn.close(); raise ValueError("This endpoint handles student requests only.")
    if req["faculty_status"] != "PENDING":
        cur.close(); conn.close(); return {"updated": False, "message": f"Already {req['faculty_status']}."}
    if not approve and (not comment or not comment.strip()):
        cur.close(); conn.close(); raise ValueError("Rejection requires a reason.")
    now = datetime.utcnow()
    try:
        c = conn.cursor()
        if approve:
            c.execute("UPDATE attendance_records SET status=%s WHERE id=%s", (req["new_status"], req["record_id"]))
            c.execute("""
                UPDATE attendance_edit_requests
                SET faculty_status='APPROVED', reviewed_by_faculty_id=%s,
                    faculty_decision_note=%s, faculty_decided_at=%s
                WHERE id=%s
            """, (faculty_id, comment, now, request_id))
            c.execute("""
                UPDATE attendance_edit_log
                SET faculty_reviewer_id=%s, faculty_reviewed_at=%s,
                    faculty_note=%s, faculty_decision='APPROVED'
                WHERE edit_request_id=%s
            """, (faculty_id, now, comment, request_id))
            conn.commit(); c.close(); cur.close(); conn.close()
            _create_notification(req["student_id"], "Your attendance correction request was approved by faculty.")
            return {"updated": True, "approved": True, "message":"Approved and applied."}
        else:
            c.execute("""
                UPDATE attendance_edit_requests
                SET faculty_status='REJECTED', reviewed_by_faculty_id=%s,
                    faculty_decision_note=%s, faculty_decided_at=%s
                WHERE id=%s
            """, (faculty_id, comment, now, request_id))
            c.execute("""
                UPDATE attendance_edit_log
                SET faculty_reviewer_id=%s, faculty_reviewed_at=%s,
                    faculty_note=%s, faculty_decision='REJECTED'
                WHERE edit_request_id=%s
            """, (faculty_id, now, comment, request_id))
            conn.commit(); c.close(); cur.close(); conn.close()
            _create_notification(req["student_id"], "Your attendance correction request was rejected by faculty.")
            return {"updated": True, "approved": False, "message":"Rejected by faculty."}
    except Exception:
        conn.rollback(); cur.close(); conn.close(); raise

def override_request_by_admin(request_id: int, admin_id: int, approve: bool, justification: str):
    if not justification or not justification.strip():
        raise ValueError("Admin override requires a justification.")
    conn = get_db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM attendance_edit_requests WHERE id=%s FOR UPDATE", (request_id,))
    req = cur.fetchone()
    if not req:
        cur.close(); conn.close(); raise ValueError("Request not found.")
    now = datetime.utcnow()
    try:
        c = conn.cursor()
        if approve:
            c.execute("UPDATE attendance_records SET status=%s WHERE id=%s", (req["new_status"], req["record_id"]))
            c.execute("""
                UPDATE attendance_edit_requests
                SET status='APPROVED', reviewed_by_admin_id=%s, reviewed_at=%s, admin_note=%s
                WHERE id=%s
            """, (admin_id, now, justification, request_id))
            c.execute("""
                UPDATE attendance_edit_log
                SET approved_by_admin_id=%s, approved_at=%s, admin_note=%s
                WHERE edit_request_id=%s
            """, (admin_id, now, justification, request_id))
            conn.commit(); c.close(); cur.close(); conn.close()
            _create_notification(req["student_id"], "An admin reviewed your attendance correction: APPROVED.")
            return {"updated": True, "approved": True, "message":"Admin approved."}
        else:
            c.execute("UPDATE attendance_records SET status=%s WHERE id=%s", (req["old_status"], req["record_id"]))
            c.execute("""
                UPDATE attendance_edit_requests
                SET status='REJECTED', reviewed_by_admin_id=%s, reviewed_at=%s, admin_note=%s
                WHERE id=%s
            """, (admin_id, now, justification, request_id))
            c.execute("""
                UPDATE attendance_edit_log
                SET approved_by_admin_id=%s, approved_at=%s, admin_note=%s
                WHERE edit_request_id=%s
            """, (admin_id, now, justification, request_id))
            conn.commit(); c.close(); cur.close(); conn.close()
            _create_notification(req["student_id"], "An admin reviewed your attendance correction: REJECTED.")
            return {"updated": True, "approved": False, "message":"Admin rejected."}
    except Exception:
        conn.rollback(); cur.close(); conn.close(); raise

def get_all_correction_requests(status_filter: str | None = None, limit: int = 500):
    conn = get_db_conn(); cur = conn.cursor(dictionary=True)
    base = """
        SELECT r.id AS request_id, r.record_id, r.session_id, r.student_id,
               r.old_status, r.new_status, r.justification,
               r.status AS admin_status, r.faculty_status, r.requested_at,
               r.reviewed_by_admin_id, r.reviewed_at, r.admin_note,
               r.reviewed_by_faculty_id, r.faculty_decided_at, r.faculty_decision_note,
               s.course, s.session_date,
               sd.full_name AS student_name, u.email AS student_email
        FROM attendance_edit_requests r
        JOIN attendance_sessions s ON s.id = r.session_id
        JOIN users u ON u.id = r.student_id
        LEFT JOIN student_details sd ON sd.user_id = r.student_id
        WHERE r.requested_by_role='STUDENT'
    """
    params = []
    if status_filter:
        base += " AND r.status=%s"
        params.append(status_filter)
    base += " ORDER BY r.requested_at DESC LIMIT %s"
    params.append(limit)
    cur.execute(base, tuple(params))
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows

def get_notifications(user_id: int, limit: int = 50):
    conn = get_db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id, message, created_at, read_at
        FROM notifications WHERE user_id=%s
        ORDER BY created_at DESC LIMIT %s
    """, (user_id, limit))
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows

def mark_notification_read(notification_id: int):
    conn = get_db_conn(); cur = conn.cursor()
    cur.execute("UPDATE notifications SET read_at=%s WHERE id=%s", (datetime.utcnow(), notification_id))
    conn.commit(); cur.close(); conn.close()

# ===================================================
# NOTIFICATION UI
# ===================================================
def show_notifications(user_id: int):
    notifs = get_notifications(user_id)
    with st.expander("🔔 Notifications", expanded=False):
        if not notifs:
            st.info("No notifications.")
        else:
            for n in notifs:
                cols = st.columns([0.8, 0.2])
                with cols[0]:
                    st.write(f"- {n['message']}  \n*{n['created_at']}*")
                with cols[1]:
                    if not n["read_at"]:
                        if st.button("Mark read", key=f"notif_{n['id']}"):
                            mark_notification_read(n["id"])
                            st.rerun()

# ===================================================
# ADMIN DASHBOARD (EXTENDED)
# ===================================================
def admin_dashboard(user):
    st.title("👑 Admin Dashboard")
    st.write(f"Logged in as *{user['email']}*")

    show_notifications(user["id"])

    conn = get_db_conn()
    cur = conn.cursor(dictionary=True)

    # Pending approvals (user registration)
    st.subheader("🕓 Pending User Approvals")
    cur.execute("SELECT * FROM users WHERE is_approved=0 ORDER BY created_at ASC;")
    pending = cur.fetchall()
    if not pending:
        st.info("No pending users.")
    else:
        for u in pending:
            st.write(f"📧 {u['email']} — Role: {u['role']}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"✅ Approve {u['email']}", key=f"a_{u['id']}"):
                    approve_user(u['id'])
                    st.success(f"Approved {u['email']}")
                    st.rerun()
            with c2:
                if st.button(f"❌ Reject {u['email']}", key=f"r_{u['id']}"):
                    reject_user(u['id'])
                    st.warning(f"Rejected {u['email']}")
                    st.rerun()

    # Manage students
    st.subheader("🎓 Manage Student Details")
    cur.execute("""
        SELECT u.id AS user_id, u.email, s.full_name, s.roll_no, s.department, s.course, s.semester, s.section
        FROM users u
        LEFT JOIN student_details s ON u.id = s.user_id
        WHERE u.role='student' AND u.is_approved=1;
    """)
    students = cur.fetchall()
    if students:
        for s in students:
            with st.form(f"student_edit_{s['user_id']}"):
                st.markdown(f"{s['email']}")
                full_name = st.text_input("Full Name", s["full_name"] or "")
                roll_no = st.text_input("Roll Number", s["roll_no"] or "")
                department = st.text_input("Department", s["department"] or "")
                course = st.text_input("Course", s["course"] or "")
                semester = st.text_input("Semester", s["semester"] or "")
                section = st.text_input("Section", s["section"] or "")
                save = st.form_submit_button("💾 Save Student Changes")
            if save:
                save_student_details(s["user_id"], full_name, roll_no, department, course, semester, section)
                st.success(f"Updated {s['email']}")
                st.rerun()
    else:
        st.info("No student details yet.")

    # Manage faculty
    st.subheader("👨‍🏫 Manage Faculty Details")
    cur.execute("""
        SELECT u.id AS user_id, u.email, f.full_name, f.faculty_id, f.department, f.course, f.designation
        FROM users u
        LEFT JOIN faculty_details f ON u.id = f.user_id
        WHERE u.role='faculty' AND u.is_approved=1;
    """)
    faculty = cur.fetchall()
    cur.close(); conn.close()
    if faculty:
        for f in faculty:
            with st.form(f"faculty_edit_{f['user_id']}"):
                st.markdown(f"{f['email']}")
                full_name = st.text_input("Full Name", f["full_name"] or "")
                faculty_id = st.text_input("Faculty ID", f["faculty_id"] or "")
                department = st.text_input("Department", f["department"] or "")
                course = st.text_input("Course", f["course"] or "")
                designation = st.text_input("Designation", f["designation"] or "")
                save = st.form_submit_button("💾 Save Faculty Changes")
            if save:
                save_faculty_details(f["user_id"], full_name, faculty_id, department, course, designation)
                st.success(f"Updated {f['email']}")
                st.rerun()
    else:
        st.info("No faculty details yet.")

    # ----------------------------
    # NEW: Admin Oversight of Student Corrections
    # ----------------------------
    st.subheader("🗂️ Attendance Corrections — Admin Oversight")
    colf1, colf2 = st.columns(2)
    with colf1:
        status_filter = st.selectbox("Filter by final admin status", ["All","PENDING","APPROVED","REJECTED"])
    with colf2:
        st.caption("Admin can override faculty decisions with justification.")

    filt = None if status_filter=="All" else status_filter
    requests = get_all_correction_requests(filt, limit=300)
    if not requests:
        st.info("No correction requests found.")
    else:
        for r in requests:
            with st.expander(f"Req#{r['request_id']} | {r['student_name'] or r['student_email']} | {r['course']} | {r['session_date']}"):
                st.write(f"Old → New: **{r['old_status']} → {r['new_status']}**")
                st.write(f"Student reason: {r['justification']}")
                st.write(f"Faculty status: **{r['faculty_status']}** — Note: {r.get('faculty_decision_note')}")
                st.write(f"Admin status: **{r['admin_status']}** — Note: {r.get('admin_note')}")
                with st.form(f"admin_override_{r['request_id']}"):
                    decision = st.selectbox("Decision", ["Approve","Reject"])
                    justification = st.text_area("Justification (required)")
                    submit = st.form_submit_button("Apply Decision")
                if submit:
                    try:
                        res = override_request_by_admin(
                            request_id=r["request_id"],
                            admin_id=user["id"],
                            approve=(decision=="Approve"),
                            justification=justification
                        )
                        st.success(res["message"])
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.page = "login"
        st.rerun()

# ===================================================
# STUDENT DASHBOARD (EXTENDED)
# ===================================================
def student_dashboard(user):
    st.title("🎓 Student Dashboard")
    show_notifications(user["id"])

    details = get_student_details(user["id"])
    if not details:
        st.info("Please complete your profile.")
        with st.form("student_form"):
            full_name = st.text_input("Full Name")
            roll_no = st.text_input("Roll Number")
            department = st.text_input("Department")
            course = st.text_input("Course")
            semester = st.text_input("Semester")
            section = st.text_input("Section")
            submit = st.form_submit_button("Save Details")
        if submit:
            save_student_details(user["id"], full_name, roll_no, department, course, semester, section)
            st.success("✅ Details saved successfully!")
            st.rerun()
    else:
        st.table(pd.DataFrame([details]))
        with st.form("update_student"):
            full_name = st.text_input("Full Name", details["full_name"])
            roll_no = st.text_input("Roll Number", details["roll_no"])
            department = st.text_input("Department", details["department"])
            course = st.text_input("Course", details["course"])
            semester = st.text_input("Semester", details["semester"])
            section = st.text_input("Section", details["section"])
            submit2 = st.form_submit_button("Update")
        if submit2:
            save_student_details(user["id"], full_name, roll_no, department, course, semester, section)
            st.success("Profile updated successfully!")
            st.rerun()

    # ----------------------------
    # NEW: Student — Request Attendance Correction (Section at bottom)
    # ----------------------------
    st.markdown("---")
    st.subheader("📌 Attendance Correction Requests")

    # List sessions the student has records for
    conn = get_db_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT s.id AS session_id, s.course, s.session_date, r.status, r.id AS record_id
        FROM attendance_records r
        JOIN attendance_sessions s ON s.id = r.session_id
        WHERE r.student_id=%s
        ORDER BY s.session_date DESC
        LIMIT 200
    """, (user["id"],))
    my_sessions = cur.fetchall(); cur.close(); conn.close()

    if not my_sessions:
        st.info("No attendance records found yet.")
    else:
        for row in my_sessions:
            with st.expander(f"{row['course']} — {row['session_date']} — Current: {row['status']}"):
                with st.form(f"req_corr_{row['session_id']}"):
                    new_status = st.selectbox("Type of correction", ["Present","Absent"], index=0 if row['status']=="Absent" else 1)
                    justification = st.text_area("Reason / Justification (min 10 characters)")
                    submit = st.form_submit_button("Request Correction")
                if submit:
                    try:
                        res = submit_correction_request(
                            student_id=user["id"],
                            session_id=row["session_id"],
                            new_status=new_status,
                            justification=justification
                        )
                        st.success("Your attendance correction request has been submitted for review.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    # Student request history
    st.subheader("📝 Your Requests")
    reqs = get_student_correction_requests(user["id"])
    if not reqs:
        st.info("No requests yet.")
    else:
        df = pd.DataFrame(reqs)
        st.dataframe(df, use_container_width=True)

    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.page = "login"
        st.rerun()

# ===================================================
# FACULTY DASHBOARD (EXTENDED)
# ===================================================
def faculty_dashboard(user):
    st.title("👨‍🏫 Faculty Dashboard")
    show_notifications(user["id"])

    details = get_faculty_details(user["id"])
    if not details:
        st.info("Please complete your faculty profile.")
        with st.form("faculty_form"):
            full_name = st.text_input("Full Name")
            faculty_id = st.text_input("Faculty ID")
            department = st.text_input("Department")
            course = st.text_input("Course")
            designation = st.text_input("Designation")
            submit = st.form_submit_button("Save Details")
        if submit:
            save_faculty_details(user["id"], full_name, faculty_id, department, course, designation)
            st.success("✅ Details saved successfully!")
            st.rerun()
    else:
        st.table(pd.DataFrame([details]))
        with st.form("update_faculty"):
            full_name = st.text_input("Full Name", details["full_name"])
            faculty_id = st.text_input("Faculty ID", details["faculty_id"])
            department = st.text_input("Department", details["department"])
            course = st.text_input("Course", details["course"])
            designation = st.text_input("Designation", details["designation"])
            submit2 = st.form_submit_button("Update")
        if submit2:
            save_faculty_details(user["id"], full_name, faculty_id, department, course, designation)
            st.success("Profile updated successfully!")
            st.rerun()

    # ----------------------------
    # NEW: Faculty — Open previous sessions & edit records
    # ----------------------------
    st.markdown("---")
    st.subheader("📚 Your Attendance Sessions")
    sessions = get_past_sessions(user["id"], limit=100)
    if not sessions:
        st.info("No sessions found. (Seed some sessions/records first.)")
    else:
        for srow in sessions:
            with st.expander(f"{srow['course']} — {srow['session_date']}"):
                records = get_session_records(srow["id"])
                if not records:
                    st.caption("No records for this session.")
                else:
                    st.dataframe(pd.DataFrame(records), use_container_width=True)
                    for rec in records:
                        with st.form(f"edit_rec_{rec['record_id']}"):
                            st.write(f"Student: {rec['student_name'] or rec['student_email']} (Roll: {rec.get('roll_no')}) — Current: {rec['status']}")
                            new_status = st.selectbox("New status", ["Present","Absent"],
                                                      index=0 if rec["status"]=="Absent" else 1,
                                                      key=f"sel_{rec['record_id']}")
                            justification = st.text_area("Justification (min 10 chars)",
                                                         key=f"j_{rec['record_id']}")
                            submit = st.form_submit_button("Apply / Queue")
                        if submit:
                            try:
                                res = edit_attendance(rec["record_id"], new_status, justification, user["id"])
                                if res.get("applied"):
                                    st.success("Updated.")
                                elif res.get("approval_required"):
                                    st.info(res.get("message","Queued for admin approval."))
                                else:
                                    st.warning(res.get("message","No change."))
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

    # ----------------------------
    # NEW: Faculty — Pending student correction requests
    # ----------------------------
    st.subheader("📥 Pending Student Correction Requests")
    pend = get_faculty_pending_requests(user["id"])
    if not pend:
        st.info("No pending student requests.")
    else:
        for r in pend:
            with st.expander(f"Req#{r['request_id']} | {r['student_name'] or r['student_email']} | {r['course']} | {r['session_date']}"):
                st.write(f"Requested change: **{r['old_status']} → {r['new_status']}**")
                st.write(f"Student justification: {r['justification']}")
                with st.form(f"fac_review_{r['request_id']}"):
                    decision = st.selectbox("Decision", ["Approve","Reject"])
                    note_label = "Optional comment" if decision=="Approve" else "Rejection reason (required)"
                    comment = st.text_area(note_label)
                    submit = st.form_submit_button("Submit Decision")
                if submit:
                    try:
                        res = review_request_by_faculty(
                            request_id=r["request_id"],
                            faculty_id=user["id"],
                            approve=(decision=="Approve"),
                            comment=comment
                        )
                        if res["approved"]:
                            st.success("Approved and applied.")
                        else:
                            st.warning("Rejected.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.page = "login"
        st.rerun()

# ===================================================
# MAIN NAV / AUTH
# ===================================================
menu = ["Login", "Register", "Dashboard / Logout"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Login" and st.session_state.page == "login":
    st.header("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
    if submit:
        ok, result = login_user(email, password)
        if ok:
            st.session_state.user = result
            st.success("✅ Login successful!")
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error(result)

elif choice == "Register":
    st.header("Register")
    with st.form("register_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["student", "faculty", "admin"])
        submit = st.form_submit_button("Register")
    if submit:
        if find_user_by_email(email):
            st.warning("User already exists.")
        else:
            approved = True if role == "admin" else False
            create_user(email, password, role, approved)
            if role == "admin":
                st.success("Admin created and approved immediately.")
            else:
                st.info("Registration complete. Waiting for admin approval.")

elif choice == "Dashboard / Logout" or st.session_state.page == "dashboard":
    user = st.session_state.user
    if user:
        if user["role"] == "admin":
            admin_dashboard(user)
        elif user["role"] == "student":
            student_dashboard(user)
        elif user["role"] == "faculty":
            faculty_dashboard(user)
    else:
        st.info("Not logged in.")
        if st.button("Go to Login"):
            st.session_state.page = "login"
            st.rerun()
