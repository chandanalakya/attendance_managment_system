DROP DATABASE IF EXISTS login_db;
CREATE DATABASE login_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE login_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Faculty') NOT NULL,
    failed_attempts INT DEFAULT 0,
    is_locked BOOLEAN DEFAULT FALSE,
    last_failed_time DATETIME DEFAULT NULL
);

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20),
    student_name VARCHAR(100),
    course VARCHAR(100),
    faculty VARCHAR(100),
    attendance_percentage DECIMAL(5,2)
);

INSERT INTO users (username, password_hash, role) VALUES
('admin1', SHA2('admin123', 256), 'Admin'),
('faculty1', SHA2('faculty123', 256), 'Faculty'),
('faculty2', SHA2('faculty456', 256), 'Faculty');

INSERT INTO attendance (student_id, student_name, course, faculty, attendance_percentage) VALUES
('S001', 'Aarav Sharma', 'Data Structures', 'faculty1', 82.5),
('S002', 'Isha Patel', 'Data Structures', 'faculty1', 68.0),
('S003', 'Rahul Verma', 'Data Structures', 'faculty1', 74.5),
('S004', 'Ananya Singh', 'Database Systems', 'faculty2', 91.2),
('S005', 'Dev Mishra', 'Database Systems', 'faculty2', 58.4),
('S006', 'Nikita Reddy', 'Database Systems', 'faculty2', 77.3),
('S007', 'Karan Das', 'Machine Learning', 'faculty1', 83.7),
('S008', 'Priya Menon', 'Machine Learning', 'faculty1', 72.0),
('S009', 'Rohit Yadav', 'Machine Learning', 'faculty1', 66.9);
