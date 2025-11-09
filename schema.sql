PRAGMA foreign_keys = ON;

-- Users
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    role            TEXT NOT NULL CHECK(role IN ('student','faculty','admin')),
    name            TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL
);

-- Courses (minimal)
CREATE TABLE IF NOT EXISTS courses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL
);

-- Enrollments (student-course relation)
CREATE TABLE IF NOT EXISTS enrollments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id   INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE(student_id, course_id)
);

-- Attendance records (one per (student, course, session_datetime))
CREATE TABLE IF NOT EXISTS attendance (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id       INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    session_dt      TEXT NOT NULL, -- ISO 8601 (UTC or local but consistent)
    status          TEXT NOT NULL CHECK(status IN ('present','absent')),
    UNIQUE(student_id, course_id, session_dt)
);

-- Correction requests (immutable by students after creation)
CREATE TABLE IF NOT EXISTS attendance_corrections (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id           INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    session_dt          TEXT NOT NULL,
    requested_status    TEXT NOT NULL CHECK(requested_status IN ('present','absent')),
    reason              TEXT NOT NULL,
    status              TEXT NOT NULL CHECK(status IN ('pending','approved','rejected')),
    faculty_reviewer_id INTEGER REFERENCES users(id),
    faculty_comment     TEXT,         -- optional for approve, mandatory for reject
    admin_reviewer_id   INTEGER REFERENCES users(id),
    admin_comment       TEXT,
    created_at          TEXT NOT NULL,
    updated_at          TEXT NOT NULL,
    -- no duplicate pending or closed requests for same key
    UNIQUE(student_id, course_id, session_dt)
);

-- Audit trail for any approval/reject/override
CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id    INTEGER NOT NULL REFERENCES users(id),
    action      TEXT NOT NULL, -- 'request_submitted','faculty_approved','faculty_rejected','admin_override'
    entity      TEXT NOT NULL, -- 'attendance_correction'
    entity_id   INTEGER NOT NULL,
    details     TEXT,
    created_at  TEXT NOT NULL
);

-- Dumb notifications (email/in-app simulated)
CREATE TABLE IF NOT EXISTS notifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    channel     TEXT NOT NULL CHECK(channel IN ('email','in-app')),
    message     TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
