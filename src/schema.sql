CREATE DATABASE sams_db;
USE sams_db;

CREATE TABLE IF NOT EXISTS users (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('student','faculty','admin') NOT NULL,
  is_approved TINYINT(1) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS student_details (
  user_id BIGINT PRIMARY KEY,
  full_name VARCHAR(255),
  roll_no VARCHAR(50),
  department VARCHAR(100),
  course VARCHAR(100),
  semester VARCHAR(50),
  section VARCHAR(50),
  CONSTRAINT fk_student_user FOREIGN KEY (user_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS faculty_details (
  user_id BIGINT PRIMARY KEY,
  full_name VARCHAR(255),
  faculty_id VARCHAR(50),
  department VARCHAR(100),
  course VARCHAR(100),
  designation VARCHAR(100),
  CONSTRAINT fk_faculty_user FOREIGN KEY (user_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


ALTER TABLE attendance_edit_requests
ADD COLUMN requested_by_role ENUM('FACULTY','STUDENT') DEFAULT 'FACULTY';

ALTER TABLE attendance_edit_requests
ADD COLUMN requested_by_student_id BIGINT NULL;

ALTER TABLE attendance_edit_requests
ADD COLUMN faculty_status ENUM('PENDING','APPROVED','REJECTED') DEFAULT 'PENDING';

ALTER TABLE attendance_edit_requests
ADD COLUMN reviewed_by_faculty_id BIGINT NULL;

ALTER TABLE attendance_edit_requests
ADD COLUMN faculty_decision_note TEXT NULL;

ALTER TABLE attendance_edit_requests
ADD COLUMN faculty_decided_at DATETIME NULL;

ALTER TABLE attendance_edit_log
ADD COLUMN faculty_reviewer_id BIGINT NULL;

ALTER TABLE attendance_edit_log
ADD COLUMN faculty_reviewed_at DATETIME NULL;

ALTER TABLE attendance_edit_log
ADD COLUMN faculty_note TEXT NULL;

ALTER TABLE attendance_edit_log
ADD COLUMN faculty_decision ENUM('APPROVED','REJECTED') NULL;

DESCRIBE attendance_edit_requests;
DESCRIBE attendance_edit_log;

USE sams_db;

-- =========================
-- 1. SEED FACULTY USER
-- =========================
INSERT INTO users (email, password_hash, role, is_approved)
VALUES ('faculty1@example.com', '$2b$12$abcdefghijklmnopqrstuv', 'faculty', 1);
SELECT * FROM users WHERE role='faculty';

-- Get inserted faculty id
SET @FACULTY_ID = LAST_INSERT_ID();

INSERT INTO faculty_details (user_id, full_name, faculty_id, department, course, designation)
VALUES (@FACULTY_ID, 'Dr. Smith', 'FAC1001', 'CSE', 'Math 101', 'Professor');


-- =========================
-- 2. SEED STUDENT USERS
-- =========================
INSERT INTO users (email, password_hash, role, is_approved) VALUES
('student1@example.com', '$2b$12$abcdefghijklmnopqrstuv', 'student', 1),
('student2@example.com', '$2b$12$abcdefghijklmnopqrstuv', 'student', 1),
('student3@example.com', '$2b$12$abcdefghijklmnopqrstuv', 'student', 1);

SET @STUDENT1 = 2 ;
SET @STUDENT2 = @STUDENT1 + 1;
SET @STUDENT3 = @STUDENT1 + 2;

INSERT INTO student_details (user_id, full_name, roll_no, department, course, semester, section)
VALUES
(2, 'Alice Johnson', '21CS001', 'CSE', 'Math 101', '3', 'A'),
(3, 'Bob Miller', '21CS002', 'CSE', 'Math 101', '3', 'A'),
(4, 'Charlie Brown', '21CS003', 'CSE', 'Math 101', '3', 'A')
ON DUPLICATE KEY UPDATE
full_name = VALUES(full_name),
roll_no = VALUES(roll_no);

-- =========================
-- 3. CREATE ATTENDANCE SESSION
-- =========================
INSERT INTO attendance_sessions (faculty_id, course, session_date)
VALUES (3 , 'Math 101', NOW());

SET @SESSION_ID = LAST_INSERT_ID();

SELECT * FROM attendance_sessions;

-- =========================
-- 4. ADD ATTENDANCE RECORDS
-- =========================
INSERT INTO attendance_records (session_id, student_id, status)
VALUES
(1, 2, 'Present'),
(2, 3, 'Absent'),
(1, 4, 'Present');

SELECT '✅ Demo data inserted successfully!' AS status;

UPDATE users
SET password_hash = '$2b$12$CwTycUXWue0Thq9StjUM0uJ8bS8p96f3jWZ5E9OQj1b.tFqHh8K36'
WHERE email = 'faculty1@example.com';

