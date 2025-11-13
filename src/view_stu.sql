-- schema.sql
-- SQLite schema for attendance system

PRAGMA foreign_keys = ON;

-- Table for students
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    class TEXT
);

-- Table for subjects
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Table for attendance records
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Present','Absent')),
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- Table for audit logs (optional for your tests)
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    student_id INTEGER,
    subject_id INTEGER,
    date TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Sample students
INSERT OR IGNORE INTO students (id, roll_no, name, class) VALUES
(1, '21CSE001', 'Chitra Madarakhandi', '3CSE'),
(2, '21CSE002', 'Rohit Kumar', '3CSE');

-- Sample subjects
INSERT OR IGNORE INTO subjects (id, name) VALUES
(1, 'Mathematics'),
(2, 'Data Structures'),
(3, 'Computer Networks');

-- Sample attendance
INSERT OR IGNORE INTO attendance (student_id, subject_id, date, status) VALUES
(1, 1, '2025-11-01', 'Present'),
(1, 1, '2025-11-03', 'Absent'),
(1, 2, '2025-11-02', 'Present'),
(1, 3, '2025-11-05', 'Present'),
(2, 1, '2025-11-01', 'Absent');
