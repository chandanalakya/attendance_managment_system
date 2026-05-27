"""User Model and Operations"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import random
from src.utils.db import get_conn
from src.utils.security import hash_password

def init_sample_users():
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            
            cur.execute("""
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
                )
            """)
            
            cur.execute("""
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
                )
            """)
            
            try:
                cur.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255)")
            except:
                pass
            try:
                cur.execute("ALTER TABLE users ADD COLUMN full_name VARCHAR(255)")
            except:
                pass
            try:
                cur.execute("ALTER TABLE students ADD COLUMN student_id VARCHAR(255)")
            except:
                pass
            try:
                cur.execute("ALTER TABLE students ADD COLUMN email VARCHAR(255)")
            except:
                pass
            
            cur.execute("SELECT COUNT(*) FROM users")
            if cur.fetchone()[0] == 0:
                users = [
                    ('admin', hash_password('admin123'), 'admin', 'admin@sams.edu', 'System Administrator'),
                    ('faculty1', hash_password('faculty123'), 'faculty', 'faculty1@sams.edu', 'Dr. John Smith'),
                    ('PES2UG23CS143', hash_password('student123'), 'student', 'student1@sams.edu', 'Student One'),
                    ('PES2UG23CS165', hash_password('student123'), 'student', 'student2@sams.edu', 'Student Two')
                ]
                
                for username, password_hash, role, email, full_name in users:
                    cur.execute(
                        "INSERT INTO users (username, password_hash, role, email, full_name) VALUES (%s, %s, %s, %s, %s)",
                        (username, password_hash, role, email, full_name)
                    )
                
                cur.execute(
                    "INSERT INTO students (student_id, roll_no, full_name, email) VALUES (%s, %s, %s, %s)",
                    ('PES2UG23CS143', 'PES2UG23CS143', 'Student One', 'student1@sams.edu')
                )
                cur.execute(
                    "INSERT INTO students (student_id, roll_no, full_name, email) VALUES (%s, %s, %s, %s)",
                    ('PES2UG23CS165', 'PES2UG23CS165', 'Student Two', 'student2@sams.edu')
                )
                
                cur.execute("SELECT id FROM courses LIMIT 1")
                course_result = cur.fetchone()
                if course_result:
                    course_id = course_result[0]
                    cur.execute("SELECT id FROM students WHERE student_id IN ('PES2UG23CS143', 'PES2UG23CS165')")
                    student_results = cur.fetchall()
                    for student_result in student_results:
                        student_id = student_result[0]
                        cur.execute(
                            "INSERT IGNORE INTO enrollments (student_id, course_id) VALUES (%s, %s)",
                            (student_id, course_id)
                        )
                
                cur.execute("SELECT id FROM students LIMIT 2")
                student_ids = [row[0] for row in cur.fetchall()]
                cur.execute("SELECT id FROM courses LIMIT 2")
                course_ids = [row[0] for row in cur.fetchall()]
                
                for i in range(30):
                    attendance_date = date.today() - timedelta(days=i)
                    for student_id in student_ids:
                        for course_id in course_ids:
                            status = random.choice(['present', 'present', 'present', 'absent', 'late'])
                            cur.execute(
                                "INSERT IGNORE INTO attendance (student_id, course_id, date, status, taken_by_user_id) VALUES (%s, %s, %s, %s, %s)",
                                (student_id, course_id, attendance_date, status, 2)
                            )
                
                audit_logs = [
                    ('LOGIN', 1, '192.168.1.100', 'Admin login successful'),
                    ('ADD', 2, '192.168.1.101', 'Attendance marked for CS101'),
                    ('EDIT', 3, '192.168.1.102', 'Status changed from absent to present'),
                    ('LOGIN', 2, '192.168.1.103', 'Faculty login successful'),
                    ('LOG_MOD_ATTEMPT', 1, '192.168.1.104', 'Unauthorized audit log modification blocked')
                ]
                
                for action_type, user_id, ip_address, details in audit_logs:
                    cur.execute(
                        "INSERT INTO audit_logs (action_type, user_id, ip_address, details) VALUES (%s, %s, %s, %s)",
                        (action_type, user_id, ip_address, details)
                    )
                
                conn.commit()
    except Exception as e:
        print(f"Error initializing users: {e}")
