"""Session Management"""
import time
import streamlit as st
from config.settings import SESSION_TIMEOUT

def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.failed_attempts = 0
        st.session_state.locked_until = None
        st.session_state.last_activity = time.time()

def check_session_timeout():
    if st.session_state.authenticated and time.time() - st.session_state.last_activity > SESSION_TIMEOUT:
        st.session_state.authenticated = False
        st.rerun()
    st.session_state.last_activity = time.time()

def get_session_remaining_time() -> int:
    elapsed = time.time() - st.session_state.last_activity
    remaining = SESSION_TIMEOUT - int(elapsed)
    return max(0, remaining // 60)
