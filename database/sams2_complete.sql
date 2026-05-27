-- ================================================================
-- SAMS2 - COMPLETE DATABASE SCHEMA
-- Student Attendance Management System
-- Consolidated from all SQL files
-- ================================================================

-- ================================================================
-- MAIN SAMS2 SCHEMA (MySQL)
-- ================================================================

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin','faculty','student') NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(255),
    student_id VARCHAR(255),
    failed_attempts INT DEFAULT 0,
    locked_until DATETIME NULL,
    last_login DATETIME NULL
);

-- COURSES TABLE
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20),
    name VARCHAR(255) NOT NULL
);

-- STUDENTS TABLE
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(255),
    roll_no VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255)
);

-- ENROLLMENTS TABLE
CREATE TABLE IF NOT EXISTS enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- ATTENDANCE TABLE
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    student_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('present','absent','late','excused') NOT NULL,
    taken_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    taken_by_user_id INT,
    notes TEXT,
    FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(taken_by_user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- AUDIT LOGS TABLE
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action_type ENUM('ADD','EDIT','DELETE','LOGIN','LOGOUT','LOG_MOD_ATTEMPT') NOT NULL,
    attendance_id INT,
    user_id INT,
    ip_address VARCHAR(45),
    details TEXT,
    immutable BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(attendance_id) REFERENCES attendance(id) ON DELETE SET NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- AUDIT SECURITY EVENTS TABLE
CREATE TABLE IF NOT EXISTS audit_security_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    user_id INT,
    ip_address VARCHAR(45),
    target_table VARCHAR(100),
    operation VARCHAR(50),
    details TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ================================================================
-- LOGIN SYSTEM TABLES
-- ================================================================

-- LOGIN USERS TABLE
CREATE TABLE IF NOT EXISTS login_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student','faculty','admin') NOT NULL DEFAULT 'student',
    is_approved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- STUDENT DETAILS TABLE
CREATE TABLE IF NOT EXISTS student_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    full_name VARCHAR(255),
    roll_no VARCHAR(100),
    department VARCHAR(255),
    course VARCHAR(255),
    semester VARCHAR(50),
    section VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES login_users(id) ON DELETE CASCADE
);

-- FACULTY DETAILS TABLE
CREATE TABLE IF NOT EXISTS faculty_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    full_name VARCHAR(255),
    faculty_id VARCHAR(100),
    department VARCHAR(255),
    course VARCHAR(255),
    designation VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES login_users(id) ON DELETE CASCADE
);

-- ================================================================
-- FACULTY ADMIN TABLES
-- ================================================================

-- FACULTY TABLE
CREATE TABLE IF NOT EXISTS faculty (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100) NOT NULL
);

-- CLASS TABLE
CREATE TABLE IF NOT EXISTS class (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    faculty_id INT,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE
);

-- STUDENT TABLE (for faculty system)
CREATE TABLE IF NOT EXISTS student (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_number VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    class_id INT,
    FOREIGN KEY (class_id) REFERENCES class(id) ON DELETE CASCADE
);

-- ATTENDANCE TABLE (for faculty system)
CREATE TABLE IF NOT EXISTS faculty_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    present BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES class(id) ON DELETE CASCADE,
    UNIQUE(student_id, date, start_time, end_time)
);

-- ADMIN ATTENDANCE VIEW TABLE
CREATE TABLE IF NOT EXISTS admin_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    student_name VARCHAR(100) NOT NULL,
    course VARCHAR(100) NOT NULL,
    faculty VARCHAR(100) NOT NULL,
    attendance_percentage DECIMAL(5,2) NOT NULL
);

-- ================================================================
-- SUBJECTS TABLE (for SQLite compatibility)
-- ================================================================

CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- ================================================================
-- SAMPLE DATA
-- ================================================================

-- Insert sample users
INSERT IGNORE INTO users (username, password_hash, role, email, full_name) VALUES 
('admin', SHA2('admin123', 256), 'admin', 'admin@sams.edu', 'System Administrator'),
('faculty1', SHA2('faculty123', 256), 'faculty', 'faculty1@sams.edu', 'Dr. John Smith'),
('PES2UG23CS143', SHA2('student123', 256), 'student', 'student1@sams.edu', 'Student One'),
('PES2UG23CS165', SHA2('student123', 256), 'student', 'student2@sams.edu', 'Student Two');

-- Insert sample courses
INSERT IGNORE INTO courses (course_code, name) VALUES 
('CS101', 'Computer Science 101'),
('CS201', 'Data Structures'),
('CS301', 'Database Systems');

-- Insert sample students
INSERT IGNORE INTO students (student_id, roll_no, full_name, email) VALUES 
('PES2UG23CS143', 'PES2UG23CS143', 'Student One', 'student1@sams.edu'),
('PES2UG23CS165', 'PES2UG23CS165', 'Student Two', 'student2@sams.edu');

-- Insert sample enrollments
INSERT IGNORE INTO enrollments (student_id, course_id) VALUES 
(1, 1), (1, 2),
(2, 1), (2, 2);

-- Insert sample faculty
INSERT IGNORE INTO faculty (name, email, password) VALUES
('John Smith', 'john@college.edu', 'john123'),
('Mary Johnson', 'mary@college.edu', 'mary123');

-- Insert sample classes
INSERT IGNORE INTO class (name, faculty_id) VALUES
('B.Tech CSE - A', 1),
('B.Tech CSE - B', 2);

-- Insert sample students for faculty system
INSERT IGNORE INTO student (roll_number, name, class_id) VALUES
('CS001', 'Aarav Sharma', 1),
('CS002', 'Isha Patel', 1),
('CS003', 'Rahul Verma', 1),
('CS004', 'Ananya Singh', 2),
('CS005', 'Dev Mishra', 2);

-- Insert sample admin attendance data
INSERT IGNORE INTO admin_attendance (student_id, student_name, course, faculty, attendance_percentage) VALUES
('S001', 'Aarav Sharma', 'Data Structures', 'Dr. John Smith', 82.5),
('S002', 'Isha Patel', 'Data Structures', 'Dr. John Smith', 68.0),
('S003', 'Rahul Verma', 'Data Structures', 'Dr. John Smith', 74.5),
('S004', 'Ananya Singh', 'Database Systems', 'Dr. Mary Johnson', 91.2),
('S005', 'Dev Mishra', 'Database Systems', 'Dr. Mary Johnson', 58.4),
('S006', 'Nikita Reddy', 'Database Systems', 'Dr. Mary Johnson', 77.3),
('S007', 'Karan Das', 'Machine Learning', 'Dr. John Smith', 83.7),
('S008', 'Priya Menon', 'Machine Learning', 'Dr. John Smith', 72.0),
('S009', 'Rohit Yadav', 'Machine Learning', 'Dr. John Smith', 66.9);

-- Insert sample subjects
INSERT IGNORE INTO subjects (name) VALUES
('Mathematics'),
('Physics'),
('Computer Science'),
('Data Structures'),
('Computer Networks');

-- PENDING USERS TABLE
CREATE TABLE IF NOT EXISTS pending_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(255),
    course_id INT,
    department VARCHAR(255),
    phone VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- PENDING EDITS TABLE
CREATE TABLE IF NOT EXISTS pending_edits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attendance_id INT NOT NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    faculty_id INT,
    justification TEXT,
    request_type VARCHAR(50) DEFAULT 'faculty',
    status VARCHAR(50) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample audit logs
INSERT IGNORE INTO audit_logs (action_type, user_id, ip_address, details) VALUES
('LOGIN', 1, '192.168.1.100', 'Admin login successful'),
('ADD', 2, '192.168.1.101', 'Attendance marked for CS101'),
('EDIT', 3, '192.168.1.102', 'Status changed from absent to present'),
('LOGIN', 2, '192.168.1.103', 'Faculty login successful'),
('LOG_MOD_ATTEMPT', 1, '192.168.1.104', 'Unauthorized audit log modification blocked');