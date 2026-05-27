"""Security Utilities"""
import hashlib
import time
import streamlit as st
from config.settings import ACCOUNT_LOCK_DURATION, MAX_LOGIN_ATTEMPTS

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_account_lock() -> bool:
    if st.session_state.locked_until and time.time() < st.session_state.locked_until:
        return True
    return False

def get_lock_remaining_time() -> tuple:
    if not st.session_state.locked_until:
        return 0, 0
    remaining_time = int(st.session_state.locked_until - time.time())
    return remaining_time // 60, remaining_time % 60

def increment_failed_attempts() -> str:
    st.session_state.failed_attempts += 1
    if st.session_state.failed_attempts >= MAX_LOGIN_ATTEMPTS:
        st.session_state.locked_until = time.time() + ACCOUNT_LOCK_DURATION
        return f"Account locked after {MAX_LOGIN_ATTEMPTS} failed attempts."
    remaining = MAX_LOGIN_ATTEMPTS - st.session_state.failed_attempts
    return f"Invalid credentials. {remaining} attempts remaining."

def reset_failed_attempts():
    st.session_state.failed_attempts = 0
    st.session_state.locked_until = None
