-- ====================================================
-- 🎓 ATTENDANCE MANAGEMENT SYSTEM (Faculty Version)
-- User Story:
-- "As faculty, I want to mark attendance for each class
--  in real time, selecting date and time duration"
-- ====================================================

DROP DATABASE IF EXISTS attendance_db;
CREATE DATABASE attendance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE attendance_db;

-- ========== FACULTY TABLE ==========
CREATE TABLE faculty (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100) NOT NULL
);

-- ========== CLASS TABLE ==========
CREATE TABLE class (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    faculty_id INT,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE
);

-- ========== STUDENT TABLE ==========
CREATE TABLE student (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_number VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    class_id INT,
    FOREIGN KEY (class_id) REFERENCES class(id) ON DELETE CASCADE
);

-- ========== ATTENDANCE TABLE ==========
CREATE TABLE attendance (
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

-- ========== SAMPLE DATA ==========
INSERT INTO faculty (name, email, password)
VALUES
('John Smith', 'john@college.edu', 'john123'),
('Mary Johnson', 'mary@college.edu', 'mary123');

INSERT INTO class (name, faculty_id)
VALUES
('B.Tech CSE - A', 1),
('B.Tech CSE - B', 2);

INSERT INTO student (roll_number, name, class_id)
VALUES
('CS001', 'Aarav Sharma', 1),
('CS002', 'Isha Patel', 1),
('CS003', 'Rahul Verma', 1),
('CS004', 'Ananya Singh', 2),
('CS005', 'Dev Mishra', 2);
