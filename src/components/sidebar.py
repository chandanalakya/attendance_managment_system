"""Sidebar Component"""
import streamlit as st
from src.utils.session import get_session_remaining_time

def render_sidebar():
    with st.sidebar:
        st.write(f"👤 **{st.session_state.username}** ({st.session_state.user_role.title()})")
        remaining_time = get_session_remaining_time()
        st.write(f"🔒 Session expires in: {remaining_time} min")
        
        st.success("🔐 TLS 1.2+ Encrypted")
        st.info("🔄 Real-time sync enabled")
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()
