import streamlit as st
import pandas as pd
import hashlib
import datetime
import os

# ==========================================================
#  Detect if running inside GitHub Actions (CI/CD environment)
# ==========================================================
IS_CI = os.getenv("GITHUB_ACTIONS") == "true"

# ==========================================================
#  Streamlit Config
# ==========================================================
st.set_page_config(page_title="Attendance Dashboard", layout="wide")
LOCK_DURATION = datetime.timedelta(minutes=30)  # Unlock after 30 mins


# ==========================================================
#  Database Connection (mocked in CI)
# ==========================================================
def get_connection():
    if IS_CI:
        print("🧪 Mocking MySQL connection in CI...")
        class MockCursor:
            def execute(self, *a, **k): pass
            def fetchone(self): return [0]
            def fetchall(self): return []
            def close(self): pass

        class MockConn:
            def cursor(self, *a, **k): return MockCursor()
            def commit(self): pass
            def close(self): pass

        return MockConn()
    else:
        import mysql.connector
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Lakshmireddy@1",  # 🔒 replace with your local MySQL password
            database="login_db"
        )


# ==========================================================
#  Password Hashing
# ==========================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ==========================================================
#  Database Setup (skipped in CI/CD)
# ==========================================================
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

    # Sample users
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users = [
            ("admin1", hash_password("admin123"), "Admin"),
            ("faculty1", hash_password("faculty123"), "Faculty"),
            ("faculty2", hash_password("faculty456"), "Faculty")
        ]
        cursor.executemany(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", users)
        conn.commit()

    # Sample attendance
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


# ==========================================================
#  User Verification with Lockout Logic
# ==========================================================
def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True) if not IS_CI else conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return False, "❌ Invalid username"

    if not IS_CI and user["is_locked"]:
        if user["last_failed_time"]:
            last = user["last_failed_time"]
            if datetime.datetime.now() - last > LOCK_DURATION:
                cursor.execute(
                    "UPDATE users SET is_locked=FALSE, failed_attempts=0, last_failed_time=NULL WHERE username=%s",
                    (username,)
                )
                conn.commit()
                conn.close()
                return False, "✅ Account automatically unlocked. Try again."
        conn.close()
        return False, "🔒 Account locked. Try after 30 minutes."

    if hash_password(password) == user["password_hash"]:
        if not IS_CI:
            cursor.execute("UPDATE users SET failed_attempts=0, last_failed_time=NULL WHERE username=%s", (username,))
            conn.commit()
        conn.close()
        return True, user["role"]

    if not IS_CI:
        new_attempts = user["failed_attempts"] + 1
        locked = new_attempts >= 5
        cursor.execute(
            "UPDATE users SET failed_attempts=%s, is_locked=%s, last_failed_time=NOW() WHERE username=%s",
            (new_attempts, locked, username)
        )
        conn.commit()
        conn.close()
        return False, "🔒 Account locked after 5 failed attempts." if locked else f"❌ Wrong password. Attempts left: {5 - new_attempts}"

    conn.close()
    return False, "❌ Invalid login (mocked CI mode)"


# ==========================================================
#  Attendance Loader
# ==========================================================
@st.cache_data
def load_attendance():
    conn = get_connection()
    query = "SELECT student_id, student_name, course, faculty, attendance_percentage FROM attendance"
    if IS_CI:
        # Mocked CI dataset
        return pd.DataFrame([{
            "student_id": "S001",
            "student_name": "Aarav Sharma",
            "course": "Mock Course",
            "faculty": "faculty1",
            "attendance_percentage": 85.0
        }])
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# ==========================================================
#  Setup (Skip in CI/CD)
# ==========================================================
if not IS_CI:
    setup_database()
else:
    print("🚀 CI mode: Skipping MySQL setup.")


# ==========================================================
#  Streamlit UI
# ==========================================================
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
                st.dataframe(faculty_data[["student_id", "student_name", "attendance_percentage"]].sort_values(by="student_id"))

        elif role == "Admin":
            st.subheader("🧑‍💼 Admin Dashboard")
            selected_course = st.selectbox("Select Course to Review:", df["course"].unique())
            low_attendance = df[(df["course"] == selected_course) & (df["attendance_percentage"] < 75)]

            if low_attendance.empty:
                st.success(f"✅ All students in {selected_course} have ≥75% attendance.")
            else:
                st.error(f"⚠️ Students below 75% in {selected_course}:")
                st.dataframe(low_attendance[["student_id", "student_name", "attendance_percentage"]].sort_values(by="attendance_percentage"))
    else:
        st.error(info)
