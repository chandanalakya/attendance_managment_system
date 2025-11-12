-- ========================
-- MySQL-compatible schema
-- ========================

-- Users
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    role            ENUM('student','faculty','admin') NOT NULL,
    name            VARCHAR(255) NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    is_approved     TINYINT(1) DEFAULT 0
);

-- Courses (minimal)
CREATE TABLE IF NOT EXISTS courses (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    code        VARCHAR(50) NOT NULL UNIQUE,
    name        VARCHAR(255) NOT NULL
);

-- Enrollments (student-course relation)
CREATE TABLE IF NOT EXISTS enrollments (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT NOT NULL,
    course_id   INT NOT NULL,
    UNIQUE(student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- Attendance records
CREATE TABLE IF NOT EXISTS attendance (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT NOT NULL,
    course_id   INT NOT NULL,
    session_dt  DATETIME NOT NULL,
    status      ENUM('present','absent') NOT NULL,
    UNIQUE(student_id, course_id, session_dt),
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- Correction requests
CREATE TABLE IF NOT EXISTS attendance_corrections (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    student_id          INT NOT NULL,
    course_id           INT NOT NULL,
    session_dt          DATETIME NOT NULL,
    requested_status    ENUM('present','absent') NOT NULL,
    reason              TEXT NOT NULL,
    status              ENUM('pending','approved','rejected') NOT NULL,
    faculty_reviewer_id INT,
    faculty_comment     TEXT,
    admin_reviewer_id   INT,
    admin_comment       TEXT,
    created_at          DATETIME NOT NULL,
    updated_at          DATETIME NOT NULL,
    UNIQUE(student_id, course_id, session_dt),
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_reviewer_id) REFERENCES users(id),
    FOREIGN KEY (admin_reviewer_id) REFERENCES users(id)
);

-- Audit trail
CREATE TABLE IF NOT EXISTS audit_log (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    actor_id    INT NOT NULL,
    action      VARCHAR(50) NOT NULL,
    entity      VARCHAR(50) NOT NULL,
    entity_id   INT NOT NULL,
    details     TEXT,
    created_at  DATETIME NOT NULL,
    FOREIGN KEY (actor_id) REFERENCES users(id)
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    channel     ENUM('email','in-app') NOT NULL,
    message     TEXT NOT NULL,
    created_at  DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
