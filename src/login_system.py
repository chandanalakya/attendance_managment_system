import streamlit as st
import pandas as pd
import mysql.connector
import hashlib
import datetime

# ---------- CONFIG ----------
st.set_page_config(page_title="Attendance Dashboard", layout="wide")
LOCK_DURATION = datetime.timedelta(minutes=30)  # ⏱️ Unlock after 30 minutes

# ---------- DATABASE CONNECTION ----------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # your MySQL username
        password="Lakshmireddy@1",  # your MySQL password
        database="login_db"  # ✅ database name
    )

# ---------- PASSWORD HASH ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------- INITIAL SETUP ----------
def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role ENUM('Admin', 'Faculty') NOT NULL,
        failed_attempts INT DEFAULT 0,
        is_locked BOOLEAN DEFAULT FALSE,
        last_failed_time DATETIME DEFAULT NULL
    )
    """)

    # ATTENDANCE TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(20),
        student_name VARCHAR(100),
        course VARCHAR(100),
        faculty VARCHAR(100),
        attendance_percentage DECIMAL(5,2)
    )
    """)

    # Insert sample users if table empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users = [
            ("admin1", hash_password("admin123"), "Admin"),
            ("faculty1", hash_password("faculty123"), "Faculty"),
            ("faculty2", hash_password("faculty456"), "Faculty")
        ]
        cursor.executemany("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", users)
        conn.commit()

    # Insert sample attendance data if table empty
    cursor.execute("SELECT COUNT(*) FROM attendance")
    if cursor.fetchone()[0] == 0:
        data = [
            ('S001', 'Aarav Sharma', 'Data Structures', 'faculty1', 82.5),
            ('S002', 'Isha Patel', 'Data Structures', 'faculty1', 68.0),
            ('S003', 'Rahul Verma', 'Data Structures', 'faculty1', 74.5),
            ('S004', 'Ananya Singh', 'Database Systems', 'faculty2', 91.2),
            ('S005', 'Dev Mishra', 'Database Systems', 'faculty2', 58.4),
            ('S006', 'Nikita Reddy', 'Database Systems', 'faculty2', 77.3),
            ('S007', 'Karan Das', 'Machine Learning', 'faculty1', 83.7),
            ('S008', 'Priya Menon', 'Machine Learning', 'faculty1', 72.0),
            ('S009', 'Rohit Yadav', 'Machine Learning', 'faculty1', 66.9)
        ]
        cursor.executemany("""
            INSERT INTO attendance (student_id, student_name, course, faculty, attendance_percentage)
            VALUES (%s, %s, %s, %s, %s)
        """, data)
        conn.commit()

    conn.close()

# ---------- VERIFY USER ----------
def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return False, "❌ Invalid username"

    # If account is locked, check if 30 mins passed
    if user["is_locked"]:
        if user["last_failed_time"]:
            last = user["last_failed_time"]
            if datetime.datetime.now() - last > LOCK_DURATION:
                # Unlock automatically
                cursor.execute(
                    "UPDATE users SET is_locked=FALSE, failed_attempts=0, last_failed_time=NULL WHERE username=%s",
                    (username,)
                )
                conn.commit()
                conn.close()
                return False, "✅ Account automatically unlocked. Please try logging in again."
        conn.close()
        return False, "🔒 Account locked due to too many failed attempts. Try again later."

    # If password is correct
    if hash_password(password) == user["password_hash"]:
        cursor.execute("UPDATE users SET failed_attempts=0, last_failed_time=NULL WHERE username=%s", (username,))
        conn.commit()
        conn.close()
        return True, user["role"]
    else:
        # Wrong password attempt
        new_attempts = user["failed_attempts"] + 1
        locked = new_attempts >= 5
        cursor.execute(
            "UPDATE users SET failed_attempts=%s, is_locked=%s, last_failed_time=NOW() WHERE username=%s",
            (new_attempts, locked, username)
        )
        conn.commit()
        conn.close()

        if locked:
            return False, "🔒 Account locked after 5 failed attempts. Please wait 30 minutes."
        else:
            return False, f"❌ Wrong password. Attempts left: {5 - new_attempts}"

# ---------- LOAD ATTENDANCE ----------
@st.cache_data
def load_attendance():
    conn = get_connection()
    query = "SELECT student_id, student_name, course, faculty, attendance_percentage FROM attendance"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ---------- MAIN APP ----------
setup_database()
st.title("🎓 Student Attendance Management System")

st.sidebar.header("🔐 Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_btn = st.sidebar.button("Login")

if login_btn:
    success, info = verify_user(username, password)

    if success:
        st.success(f"✅ Login successful! Welcome, {username}.")
        role = info
        df = load_attendance()

        if role == "Faculty":
            st.subheader("👩‍🏫 Faculty Dashboard")

            faculty_courses = df[df["faculty"] == username]["course"].unique()
            if len(faculty_courses) == 0:
                st.info("No courses assigned to you.")
            else:
                selected_course = st.selectbox("Select Course:", faculty_courses)
                faculty_data = df[(df["faculty"] == username) & (df["course"] == selected_course)]

                st.write(f"### Students in {selected_course}")
                st.dataframe(
                    faculty_data[["student_id", "student_name", "attendance_percentage"]]
                    .sort_values(by="student_id")
                )

        elif role == "Admin":
            st.subheader("🧑‍💼 Admin Dashboard")

            selected_course = st.selectbox("Select Course to Review:", df["course"].unique())
            low_attendance = df[(df["course"] == selected_course) & (df["attendance_percentage"] < 75)]

            if low_attendance.empty:
                st.success(f"✅ All students in {selected_course} have ≥75% attendance.")
            else:
                st.error(f"⚠️ Students below 75% in {selected_course}:")
                st.dataframe(
                    low_attendance[["student_id", "student_name", "attendance_percentage"]]
                    .sort_values(by="attendance_percentage")
                )
    else:
        st.error(info)
