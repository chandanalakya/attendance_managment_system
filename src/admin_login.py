import streamlit as st
import mysql.connector
import bcrypt
import os
from dotenv import load_dotenv
import pathlib

# -------------------------------
# Load environment variables
# -------------------------------
env_path = pathlib.Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "sams_db")

st.set_page_config(page_title="Admin — Attendance Management", layout="wide")

# -------------------------------
# Session initialization
# -------------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# -------------------------------
# Database connection
# -------------------------------
def get_db_conn():
    return mysql.connector.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASS,
        database=DB_NAME, auth_plugin="mysql_native_password"
    )

# -------------------------------
# Helper functions
# -------------------------------
def find_user_by_email(email):
    conn = get_db_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def create_user(email, password, role="admin", approved=True):
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (email, password_hash, role, is_approved) VALUES (%s,%s,%s,%s)",
        (email, pw_hash, role, approved)
    )
    conn.commit()
    cur.close()
    conn.close()

def approve_user(user_id):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_approved=TRUE WHERE id=%s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def reject_user(user_id):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def verify_password(pw, pw_hash):
    return bcrypt.checkpw(pw.encode(), pw_hash.encode())

def login_user(email, password):
    user = find_user_by_email(email)
    if not user:
        return False, "No such user."
    if not user["is_approved"]:
        return False, "Account pending admin approval."
    if verify_password(password, user["password_hash"]):
        return True, user
    return False, "Invalid password."

# -------------------------------
# Admin Dashboard
# -------------------------------
def admin_dashboard(user):
    st.title("👑 Admin Dashboard")
    st.write(f"Logged in as *{user['email']}*")

    conn = get_db_conn()
    cur = conn.cursor(dictionary=True)

    # Pending approvals
    st.subheader("🕓 Pending Approvals")
    cur.execute("SELECT * FROM users WHERE is_approved=0 ORDER BY created_at ASC;")
    pending = cur.fetchall()
    if not pending:
        st.info("No pending users.")
    else:
        for u in pending:
            st.write(f"📧 {u['email']} — Role: {u['role']}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"✅ Approve {u['email']}", key=f"a_{u['id']}"):
                    approve_user(u['id'])
                    st.success(f"Approved {u['email']}")
                    st.rerun()

            with c2:
                if st.button(f"❌ Reject {u['email']}", key=f"r_{u['id']}"):
                    reject_user(u['id'])
                    st.warning(f"Rejected {u['email']}")
                    st.rerun()


    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.page = "login"
        st.rerun()


# -------------------------------
# Main Logic
# -------------------------------
menu = ["Login", "Register", "Dashboard / Logout"]
choice = st.sidebar.selectbox("Navigation", menu)

# ---------- LOGIN ----------
if choice == "Login" and st.session_state.page == "login":
    st.header("Admin Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
    if submit:
        ok, result = login_user(email, password)
        if ok and result["role"] == "admin":
            st.session_state.user = result
            st.success("✅ Login successful!")
            st.session_state.page = "dashboard"
            st.rerun()

        else:
            st.error(result or "Only admin can login here.")

# ---------- REGISTER ----------
elif choice == "Register":
    st.header("Register Admin")
    with st.form("register_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Register")
    if submit:
        if find_user_by_email(email):
            st.warning("User already exists.")
        else:
            create_user(email, password)
            st.success("Admin created successfully and approved immediately!")

# ---------- DASHBOARD ----------
elif choice == "Dashboard / Logout" or st.session_state.page == "dashboard":
    user = st.session_state.user
    if user and user["role"] == "admin":
        admin_dashboard(user)
    else:
        st.info("Not logged in or not an admin.")
        if st.button("Go to Login"):
            st.session_state.page = "login"
            st.rerun()

