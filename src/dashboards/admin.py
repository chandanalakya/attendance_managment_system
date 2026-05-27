"""Admin Dashboard"""
import streamlit as st
import pandas as pd
import time
import plotly.express as px
from src.utils.db import get_conn
from config.settings import DEFAULT_ATTENDANCE_THRESHOLD, MAX_AUDIT_LOGS

def admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "🚨 Defaulters", "🔍 Audit Logs", "📈 Analytics", "👥 Approvals"])
    
    with tab1:
        render_overview()
    with tab2:
        render_defaulters()
    with tab3:
        render_audit_logs()
    with tab4:
        render_analytics()
    with tab5:
        render_approvals()

def render_overview():
    col1, col2, col3, col4 = st.columns(4)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM students")
        col1.metric("Total Students", cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM courses")
        col2.metric("Total Courses", cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM attendance WHERE date = CURDATE()")
        col3.metric("Today's Records", cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM users")
        col4.metric("Active Users", cur.fetchone()[0])

def render_defaulters():
    st.subheader("🚨 Defaulter Management")
    threshold = st.slider("Attendance Threshold (%)", 50, 90, DEFAULT_ATTENDANCE_THRESHOLD)
    
    with get_conn() as conn:
        query = """
        SELECT s.roll_no, s.full_name, c.name as course,
               COUNT(a.id) as total_classes,
               SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as present,
               ROUND(SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.id), 2) as percentage
        FROM students s
        JOIN attendance a ON s.id = a.student_id
        JOIN courses c ON a.course_id = c.id
        GROUP BY s.id, c.id
        HAVING percentage < %s
        ORDER BY percentage ASC
        """
        defaulters_df = pd.read_sql(query, conn, params=[threshold])
        
        if not defaulters_df.empty:
            st.error(f"⚠️ {len(defaulters_df)} students below {threshold}% attendance")
            st.dataframe(defaulters_df, use_container_width=True)
        else:
            st.success(f"✅ All students above {threshold}% attendance threshold")

def render_audit_logs():
    st.subheader("🔍 Audit Log Monitoring")
    with get_conn() as conn:
        query = f"""
        SELECT al.created_at, al.action_type, u.username, al.ip_address, al.details
        FROM audit_logs al
        LEFT JOIN users u ON al.user_id = u.id
        WHERE al.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        AND (al.action_type != 'ADD' OR al.created_at <= DATE_SUB(NOW(), INTERVAL 24 HOUR))
        ORDER BY al.created_at DESC LIMIT {MAX_AUDIT_LOGS}
        """
        audit_df = pd.read_sql(query, conn)
        st.dataframe(audit_df, use_container_width=True)
        st.info("🔒 Attendance marking logs appear after 24 hours for security")

def render_analytics():
    st.subheader("📈 Analytics Dashboard")
    with get_conn() as conn:
        trend_query = """
        SELECT date, 
               AVG(CASE WHEN status = 'present' THEN 100 ELSE 0 END) as avg_attendance
        FROM attendance 
        WHERE date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY date
        ORDER BY date
        """
        trend_df = pd.read_sql(trend_query, conn)
        
        if not trend_df.empty:
            fig = px.line(trend_df, x='date', y='avg_attendance', title='30-Day Attendance Trend')
            st.plotly_chart(fig, use_container_width=True)

def render_approvals():
    st.subheader("👥 User Registration Approvals")
    with get_conn() as conn:
        pending_df = pd.read_sql("SELECT * FROM pending_users WHERE status = 'pending' ORDER BY created_at DESC", conn)
        
        if not pending_df.empty:
            for _, user in pending_df.iterrows():
                with st.expander(f"{user['username']} - {user['role'].title()}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    col1.write(f"**Name:** {user['full_name']}")
                    col1.write(f"**Email:** {user['email']}")
                    col1.write(f"**Department:** {user['department']}")
                    
                    if col2.button("✅ Approve", key=f"approve_{user['id']}"):
                        approve_user(user)
                    if col3.button("❌ Reject", key=f"reject_{user['id']}"):
                        reject_user(user['id'])
        else:
            st.info("No pending registrations")
    
    st.divider()
    render_edit_approvals()

def approve_user(user):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password_hash, role, email, full_name) VALUES (%s, %s, %s, %s, %s)",
                (user['username'], user['password_hash'], user['role'], user['email'], user['full_name']))
            
            if user['role'] == 'student':
                cur.execute("INSERT INTO students (student_id, roll_no, full_name, email) VALUES (%s, %s, %s, %s)",
                    (user['username'], user['username'], user['full_name'], user['email']))
                if user['course_id']:
                    student_id = cur.lastrowid
                    cur.execute("INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s)",
                        (student_id, int(user['course_id'])))
            
            cur.execute("UPDATE pending_users SET status = 'approved' WHERE id = %s", (int(user['id']),))
            conn.commit()
            st.success(f"✅ {user['username']} approved!")
            time.sleep(1)
            st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

def reject_user(user_id):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE pending_users SET status = 'rejected' WHERE id = %s", (int(user_id),))
            conn.commit()
            st.success("❌ User rejected")
            time.sleep(1)
            st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

def render_edit_approvals():
    st.subheader("✏️ Attendance Edit Approvals")
    with get_conn() as conn:
        edit_query = """
        SELECT pe.*, s.roll_no, s.full_name, c.name as course, 
               COALESCE(u.username, 'Student Request') as faculty,
               a.date, a.status as current_status, pe.request_type
        FROM pending_edits pe
        JOIN attendance a ON pe.attendance_id = a.id
        JOIN students s ON a.student_id = s.id
        JOIN courses c ON a.course_id = c.id
        LEFT JOIN users u ON pe.faculty_id = u.id
        WHERE pe.status = 'pending'
        ORDER BY pe.created_at DESC
        """
        edit_df = pd.read_sql(edit_query, conn)
        
        if not edit_df.empty:
            for _, edit in edit_df.iterrows():
                with st.expander(f"{edit['roll_no']} - {edit['course']} - {edit['date']}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    col1.write(f"**Student:** {edit['full_name']}")
                    col1.write(f"**Requested by:** {edit['faculty']}")
                    col1.write(f"**Change:** {edit['old_status']} → {edit['new_status']}")
                    col1.write(f"**Reason:** {edit['justification']}")
                    
                    if col2.button("✅ Approve", key=f"approve_edit_{edit['id']}"):
                        approve_edit(edit)
                    if col3.button("❌ Reject", key=f"reject_edit_{edit['id']}"):
                        reject_edit(edit['id'])
        else:
            st.info("No pending edit requests")

def approve_edit(edit):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE attendance SET status = %s WHERE id = %s",
                (edit['new_status'].lower(), int(edit['attendance_id'])))
            cur.execute("UPDATE pending_edits SET status = 'approved' WHERE id = %s", (int(edit['id']),))
            conn.commit()
            st.toast("✅ Edit approved!", icon="✅")
            st.rerun()
    except Exception as e:
        st.toast(f"❌ Error: {str(e)[:30]}...", icon="❌")

def reject_edit(edit_id):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE pending_edits SET status = 'rejected' WHERE id = %s", (int(edit_id),))
            conn.commit()
            st.toast("❌ Edit rejected", icon="❌")
            st.rerun()
    except Exception as e:
        st.toast(f"❌ Error: {str(e)[:30]}...", icon="❌")
