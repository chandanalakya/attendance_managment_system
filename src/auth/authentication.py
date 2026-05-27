"""Authentication Logic"""
import streamlit as st
import time
from src.utils.db import get_conn
from src.utils.security import hash_password, check_account_lock, get_lock_remaining_time, increment_failed_attempts, reset_failed_attempts
from src.auth.signup import signup_page

def authenticate(username: str, password: str, role: str) -> tuple:
    if check_account_lock():
        return None, "Account locked due to failed attempts. Try again later."
    
    hashed_password = hash_password(password)
    
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, username, role FROM users WHERE username = %s AND password_hash = %s AND role = %s",
                (username, hashed_password, role)
            )
            user = cur.fetchone()
            
            if user:
                reset_failed_attempts()
                return {'id': user[0], 'username': user[1], 'role': user[2]}, None
            else:
                error_msg = increment_failed_attempts()
                return None, error_msg
                
    except Exception as e:
        return None, f"Authentication error: {e}"

def login_page():
    st.title("🎓 SAMS2 - Student Attendance Management System")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        st.subheader("🔐 Secure Login")
        
        if check_account_lock():
            minutes, seconds = get_lock_remaining_time()
            st.error(f"🔒 Account locked. Try again in {minutes}:{seconds:02d}")
            return
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            role = st.selectbox("Select Role", ["admin", "faculty", "student"])
            username = st.text_input("Institutional ID")
            password = st.text_input("Password", type="password")
            
            st.info("🔒 Secure login with TLS 1.2+ encryption. Account locks after 5 failed attempts.")
            
            if st.button("🔑 Login", use_container_width=True):
                if username and password:
                    user, error = authenticate(username, password, role)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_role = user['role']
                        st.session_state.user_id = user['id']
                        st.session_state.username = user['username']
                        st.success(f"✅ Welcome {user['username']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
                else:
                    st.warning("Please enter both username and password")
    
    with tab2:
        signup_page()
