"""SAMS2 - Main Application Entry Point"""
import streamlit as st
import os
from src.utils.db import test_connection, init_db
from src.utils.session import init_session_state, check_session_timeout
from src.auth.authentication import login_page
from src.dashboards.admin import admin_dashboard
from src.dashboards.faculty import faculty_dashboard
from src.dashboards.student import student_dashboard
from src.components.sidebar import render_sidebar
from src.models.user import init_sample_users

st.set_page_config(page_title="SAMS2", page_icon="🎓", layout="wide")

def initialize_database():
    if 'db_initialized' not in st.session_state:
        success, message = test_connection()
        if not success:
            st.error(f"❌ {message}")
            st.stop()
        try:
            init_db(os.path.join("database", "sams2_complete.sql"))
            st.session_state.db_initialized = True
        except Exception as e:
            st.error(f"Database initialization failed: {e}")
            st.stop()

def main():
    initialize_database()
    init_session_state()
    init_sample_users()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        check_session_timeout()
        render_sidebar()
        
        if st.session_state.user_role == 'admin':
            admin_dashboard()
        elif st.session_state.user_role == 'faculty':
            faculty_dashboard()
        elif st.session_state.user_role == 'student':
            student_dashboard()

if __name__ == "__main__":
    main()
