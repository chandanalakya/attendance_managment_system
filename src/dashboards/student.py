"""Student Dashboard"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from src.utils.db import get_conn
from config.settings import WARNING_THRESHOLD, DEFAULT_ATTENDANCE_THRESHOLD

def student_dashboard():
    st.title("🎓 Student Dashboard")
    tab1, tab2 = st.tabs(["📊 Attendance Overview", "📝 Request Correction"])
    
    with tab1:
        render_attendance_overview()
    with tab2:
        render_request_correction()

def render_request_correction():
    st.subheader("📝 Request Attendance Correction")
    st.info("⏰ Requests must be made within 24 hours of class")
    
    with get_conn() as conn:
        student_query = "SELECT id FROM students WHERE student_id = %s OR roll_no = %s"
        student_df = pd.read_sql(student_query, conn, params=[st.session_state.username, st.session_state.username])
        
        if not student_df.empty:
            student_id = student_df.iloc[0]['id']
            
            recent_query = """
            SELECT a.id, c.name as course, a.status, a.date
            FROM attendance a
            JOIN courses c ON a.course_id = c.id
            WHERE a.student_id = %s 
            AND a.date >= DATE_SUB(CURDATE(), INTERVAL 1 DAY)
            AND a.status IN ('absent', 'late')
            ORDER BY a.date DESC
            """
            recent_df = pd.read_sql(recent_query, conn, params=[int(student_id)])
            
            if not recent_df.empty:
                selected_record = st.selectbox("Select Record to Request Correction",
                    recent_df.apply(lambda x: f"{x['course']} - {x['status'].upper()} - {x['date']}", axis=1))
                
                if selected_record:
                    record_idx = recent_df.index[recent_df.apply(lambda x: f"{x['course']} - {x['status'].upper()} - {x['date']}", axis=1) == selected_record][0]
                    record = recent_df.iloc[record_idx]
                    
                    col1, col2 = st.columns(2)
                    new_status = col1.selectbox("Requested Status", ["PRESENT", "EXCUSED"])
                    reason = col2.text_area("Reason for Request (Required)")
                    
                    if st.button("📤 Submit Request") and reason:
                        submit_correction_request(record, new_status, reason)
            else:
                st.info("No recent attendance records available for correction (within 24 hours)")

def submit_correction_request(record, new_status, reason):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO pending_edits (attendance_id, old_status, new_status, faculty_id, justification, request_type) VALUES (%s, %s, %s, %s, %s, 'student')",
                (int(record['id']), record['status'], new_status, st.session_state.user_id, reason))
            conn.commit()
            st.toast("📤 Request submitted for approval", icon="📤")
    except Exception as e:
        st.toast(f"❌ Error: {str(e)[:30]}...", icon="❌")

def render_attendance_overview():
    with get_conn() as conn:
        student_query = "SELECT * FROM students WHERE student_id = %s OR roll_no = %s"
        student_df = pd.read_sql(student_query, conn, params=[st.session_state.username, st.session_state.username])
        
        if not student_df.empty:
            student = student_df.iloc[0]
            student_id = student['id']
            
            st.success("🔄 Real-time data sync enabled")
            
            overall_query = """
            SELECT COUNT(a.id) as total_classes,
                   SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as present,
                   ROUND(SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.id), 2) as percentage
            FROM attendance a WHERE a.student_id = %s AND a.taken_by_user_id IS NOT NULL
            """
            overall_df = pd.read_sql(overall_query, conn, params=[int(student_id)])
            
            if not overall_df.empty and overall_df.iloc[0]['total_classes'] > 0:
                overall_pct = overall_df.iloc[0]['percentage']
                st.metric("📊 Overall Attendance", f"{overall_pct}%")
                
                if overall_pct >= DEFAULT_ATTENDANCE_THRESHOLD:
                    st.success("✅ Good Standing")
                elif overall_pct >= WARNING_THRESHOLD:
                    st.warning("⚠️ Below Average")
                else:
                    st.error("🚨 Defaulter Risk")
            
            render_subject_wise_attendance(student_id)
            render_daily_attendance(student_id, overall_df.iloc[0]['percentage'] if not overall_df.empty else 0)
        else:
            st.error("Student record not found. Please contact administrator.")

def render_subject_wise_attendance(student_id):
    st.subheader("📚 Subject-wise Attendance")
    
    with get_conn() as conn:
        subject_query = """
        SELECT c.name as course,
               COUNT(a.id) as total_classes,
               SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as present,
               ROUND(SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.id), 2) as percentage
        FROM attendance a
        JOIN courses c ON a.course_id = c.id
        WHERE a.student_id = %s
        GROUP BY c.id
        ORDER BY percentage DESC
        """
        subject_df = pd.read_sql(subject_query, conn, params=[int(student_id)])
        
        if not subject_df.empty:
            st.dataframe(subject_df, use_container_width=True)
            
            low_subjects = subject_df[subject_df['percentage'] < DEFAULT_ATTENDANCE_THRESHOLD]
            if not low_subjects.empty:
                st.error(f"🚨 Subjects needing attention (< {DEFAULT_ATTENDANCE_THRESHOLD}%):")
                for _, subject in low_subjects.iterrows():
                    st.write(f"• **{subject['course']}**: {subject['percentage']}%")

def render_daily_attendance(student_id, overall_pct):
    st.subheader("📅 Daily Attendance Status")
    
    col1, col2 = st.columns(2)
    start_date = col1.date_input("From Date", value=date.today() - timedelta(days=30))
    end_date = col2.date_input("To Date", value=date.today())
    
    with get_conn() as conn:
        daily_query = """
        SELECT a.date, c.name as course, a.status
        FROM attendance a
        JOIN courses c ON a.course_id = c.id
        WHERE a.student_id = %s AND a.date BETWEEN %s AND %s
        ORDER BY a.date DESC
        """
        daily_df = pd.read_sql(daily_query, conn, params=[int(student_id), start_date, end_date])
        
        if not daily_df.empty:
            st.dataframe(daily_df, use_container_width=True)
            
            col1, col2 = st.columns(2)
            csv_data = daily_df.to_csv(index=False)
            col1.download_button("📄 Download CSV", csv_data, f"attendance_{st.session_state.username}.csv", "text/csv")
            
            pdf_content = f"Attendance Report for {st.session_state.username}\n\n"
            pdf_content += f"Overall Attendance: {overall_pct if overall_pct else 'N/A'}%\n\n"
            pdf_content += "Daily Records:\n"
            for _, row in daily_df.iterrows():
                pdf_content += f"{row['date']} - {row['course']} - {row['status'].upper()}\n"
            
            col2.download_button("📄 Download PDF", pdf_content, f"attendance_{st.session_state.username}.txt", "text/plain")
        else:
            st.info("No attendance records found for selected date range")
