"""Registration/Signup Logic"""
import streamlit as st
import pandas as pd
from src.utils.db import get_conn
from src.utils.security import hash_password
from config.settings import MIN_PASSWORD_LENGTH

def check_registration_status(username: str):
    try:
        with get_conn() as conn:
            status_query = "SELECT status, created_at FROM pending_users WHERE username = %s"
            status_df = pd.read_sql(status_query, conn, params=[username])
            
            if not status_df.empty:
                status = status_df.iloc[0]['status']
                created_at = status_df.iloc[0]['created_at']
                
                if status == 'pending':
                    st.warning(f"⏳ Registration pending approval (submitted: {created_at})")
                elif status == 'approved':
                    st.success(f"✅ Registration approved! You can now login.")
                elif status == 'rejected':
                    st.error(f"❌ Registration rejected. Contact admin for details.")
            else:
                user_query = "SELECT username FROM users WHERE username = %s"
                user_df = pd.read_sql(user_query, conn, params=[username])
                if not user_df.empty:
                    st.success("✅ You are already registered! You can login.")
                else:
                    st.info("🔍 No registration found for this username")
    except Exception as e:
        st.error(f"Error checking status: {e}")

def signup_page():
    st.subheader("📝 Create New Account")
    st.info("⏳ All registrations require admin approval")
    
    username_check = st.text_input("🔍 Check Registration Status", placeholder="Enter your username")
    if username_check:
        check_registration_status(username_check)
    
    st.divider()
    
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            role = st.selectbox("Role", ["student", "faculty"])
            username = st.text_input("Institutional ID", placeholder="e.g., PES2UG23CS143")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
        
        with col2:
            full_name = st.text_input("Full Name")
            email = st.text_input("Email", placeholder="name@pesu.pes.edu")
            department = st.text_input("Department", value="Computer Science")
            
            if role == "student":
                with get_conn() as conn:
                    courses_df = pd.read_sql("SELECT id, course_code, name FROM courses", conn)
                    course_options = [f"{row['course_code']} - {row['name']}" for _, row in courses_df.iterrows()]
                    selected_course = st.selectbox("Select Course", course_options)
                    course_id = int(courses_df.iloc[course_options.index(selected_course)]['id']) if course_options else 1
            else:
                course_id = None
        
        phone = st.text_input("Phone Number")
        submitted = st.form_submit_button("📝 Submit Registration Request")
        
        if submitted:
            if not all([username, password, confirm_password, full_name]):
                st.error("Please fill all required fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < MIN_PASSWORD_LENGTH:
                st.error(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
            else:
                try:
                    with get_conn() as conn:
                        cur = conn.cursor()
                        
                        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                        user_exists = cur.fetchone()
                        
                        cur.execute("SELECT id FROM pending_users WHERE username = %s", (username,))
                        pending_exists = cur.fetchone()
                        
                        if user_exists or pending_exists:
                            st.error("Username already exists or pending approval")
                        else:
                            hashed_password = hash_password(password)
                            cur.execute(
                                "INSERT INTO pending_users (username, password_hash, role, email, full_name, course_id, department, phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                (username, hashed_password, role, email, full_name, course_id, department, phone)
                            )
                            conn.commit()
                            st.success("✅ Registration request submitted! Wait for admin approval.")
                            
                except Exception as e:
                    st.error(f"Registration failed: {e}")
