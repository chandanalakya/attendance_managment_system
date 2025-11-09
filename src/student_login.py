import streamlit as st
import mysql.connector
import bcrypt
import os
import pathlib
from dotenv import load_dotenv
import pandas as pd

# -----------------------
# Load environment variables
# -----------------------
env_path = pathlib.Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "sams_db")

st.set_page_config(page_title="SAMS - Student Portal", layout="wide")

# -----------------------
# Session initialization
# -----------------------
if "user" not in st.session_state:
    st.session_state.user = None

# -----------------------
# DB connection & helpers
# -----------------------
def get_db_conn():
    return mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS,
        database=DB_NAME, auth_plugin="mysql_native_password"
    )

def find_user_by_email(email):
    conn = get_db_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s AND role='student'", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def create_user(email, password):
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (email, password_hash, role, is_approved) VALUES (%s,%s,'student',0)",
        (email, pw_hash)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_student_details(user_id):
    conn = get_db_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM student_details WHERE user_id=%s", (user_id,))
    details = cur.fetchone()
    cur.close()
    conn.close()
    return details

def save_student_details(user_id, full_name, roll_no, department, course, semester, section):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO student_details (user_id, full_name, roll_no, department, course, semester, section)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
        full_name=VALUES(full_name), roll_no=VALUES(roll_no),
        department=VALUES(department), course=VALUES(course),
        semester=VALUES(semester), section=VALUES(section);
    """, (user_id, full_name, roll_no, department, course, semester, section))
    conn.commit()
    cur.close()
    conn.close()

def verify_password(pw, pw_hash):
    return bcrypt.checkpw(pw.encode(), pw_hash.encode())

# -----------------------
# Sidebar Navigation
# -----------------------
menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Navigation", menu)

# -----------------------
# Registration
# -----------------------
if choice == "Register":
    st.title("🎓 Student Registration")
    with st.form("register_form"):
        email = st.text_input("Institutional Email / ID")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Register")
    if submit:
        if find_user_by_email(email):
            st.warning("User already exists.")
        else:
            create_user(email, password)
            st.success("✅ Registration successful! Waiting for admin approval.")

# -----------------------
# Login
# -----------------------
elif choice == "Login":
    st.title("🎓 Student Login")
    if not st.session_state.user:
        with st.form("login_form"):
            email = st.text_input("Institutional Email / ID")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
        if submit:
            user = find_user_by_email(email)
            if user and user["is_approved"] and verify_password(password, user["password_hash"]):
                st.session_state.user = user
                st.success("✅ Login successful!")
            elif user and not user["is_approved"]:
                st.warning("Your account is pending admin approval.")
            else:
                st.error("Invalid credentials.")
    else:
        st.header(f"Welcome, {st.session_state.user['email']}")
        details = get_student_details(st.session_state.user["id"])
        if details:
            st.table(pd.DataFrame([details]))
        else:
            st.info("Please complete your profile.")
            with st.form("student_form"):
                full_name = st.text_input("Full Name")
                roll_no = st.text_input("Roll Number")
                department = st.text_input("Department")
                course = st.text_input("Course")
                semester = st.text_input("Semester")
                section = st.text_input("Section")
                submit_details = st.form_submit_button("Save Details")
            if submit_details:
                save_student_details(st.session_state.user["id"], full_name, roll_no, department, course, semester, section)
                st.success("✅ Profile saved successfully!")
        if st.button("Logout"):
            st.session_state.user = None
            st.experimental_rerun()
