PRAGMA foreign_keys = ON;

-- ================================================================
-- USERS TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'user'
);

-- ================================================================
-- COURSES TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- ================================================================
-- STUDENTS TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    roll_no TEXT NOT NULL UNIQUE
);

-- ================================================================
-- ENROLLMENTS TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- ================================================================
-- ATTENDANCE TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PRESENT','ABSENT','LATE','EXCUSED')),
    taken_at DATETIME NOT NULL DEFAULT (datetime('now')),
    taken_by_user_id INTEGER NOT NULL,
    notes TEXT,
    FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(taken_by_user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ================================================================
-- AUDIT LOGS TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL CHECK (action_type IN ('ADD','EDIT','DELETE','LOG_MOD_ATTEMPT')),
    attendance_id INTEGER,
    user_id INTEGER NOT NULL,
    ip_address TEXT,
    details TEXT,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(attendance_id) REFERENCES attendance(id) ON DELETE SET NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ================================================================
-- AUDIT SECURITY EVENTS TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS audit_security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    user_id INTEGER,
    ip_address TEXT,
    target_table TEXT,
    operation TEXT,
    details TEXT,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ================================================================
-- IMMUTABILITY TRIGGERS FOR AUDIT_LOGS
-- ================================================================
CREATE TRIGGER IF NOT EXISTS trg_audit_logs_prevent_update
BEFORE UPDATE ON audit_logs
BEGIN
    SELECT RAISE(ABORT, 'audit_logs are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_audit_logs_prevent_delete
BEFORE DELETE ON audit_logs
BEGIN
    SELECT RAISE(ABORT, 'audit_logs are immutable');
END;
