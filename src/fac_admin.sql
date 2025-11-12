-- ==========================================================
-- 🎓 STUDENT ATTENDANCE MANAGEMENT DASHBOARD DATABASE
-- Database: facAdm
-- ==========================================================

DROP DATABASE IF EXISTS facAdm;
CREATE DATABASE facAdm CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE facAdm;

-- ========== ATTENDANCE TABLE ==========
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    student_name VARCHAR(100) NOT NULL,
    course VARCHAR(100) NOT NULL,
    faculty VARCHAR(100) NOT NULL,
    attendance_percentage DECIMAL(5,2) NOT NULL
);

-- ========== SAMPLE DATA ==========
INSERT INTO attendance (student_id, student_name, course, faculty, attendance_percentage)
VALUES
('S001', 'Aarav Sharma', 'Data Structures', 'Dr. John Smith', 82.5),
('S002', 'Isha Patel', 'Data Structures', 'Dr. John Smith', 68.0),
('S003', 'Rahul Verma', 'Data Structures', 'Dr. John Smith', 74.5),
('S004', 'Ananya Singh', 'Database Systems', 'Dr. Mary Johnson', 91.2),
('S005', 'Dev Mishra', 'Database Systems', 'Dr. Mary Johnson', 58.4),
('S006', 'Nikita Reddy', 'Database Systems', 'Dr. Mary Johnson', 77.3),
('S007', 'Karan Das', 'Machine Learning', 'Dr. John Smith', 83.7),
('S008', 'Priya Menon', 'Machine Learning', 'Dr. John Smith', 72.0),
('S009', 'Rohit Yadav', 'Machine Learning', 'Dr. John Smith', 66.9);
