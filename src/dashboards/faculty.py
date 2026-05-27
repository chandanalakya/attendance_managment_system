"""Faculty Dashboard"""
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from src.utils.db import get_conn

def faculty_dashboard():
    st.title("👩🏫 Faculty Dashboard")
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Mark Attendance", "📊 View Records", "✏️ Edit Attendance", "📋 Reports"])
    
    with tab1:
        render_mark_attendance()
    with tab2:
        render_view_records()
    with tab3:
        render_edit_attendance()
    with tab4:
        render_reports()

def render_mark_attendance():
    st.subheader("Mark Attendance")
    schedule_mode = st.checkbox("⏰ Schedule for different date/time")
    
    with get_conn() as conn:
        courses_df = pd.read_sql("SELECT * FROM courses ORDER BY name", conn)
        
        if not courses_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                course = st.selectbox("Select Course", courses_df['name'].tolist())
                course_id = int(courses_df[courses_df['name'] == course]['id'].iloc[0])
            
            if schedule_mode:
                with col2:
                    class_date = st.date_input("Class Date", value=date.today())
                with col3:
                    class_time = st.time_input("Class Time", value=datetime.now().time())
                st.info(f"📚 Scheduled: {course} on {class_date} at {class_time}")
            else:
                class_date = date.today()
                class_time = datetime.now().time()
                st.info(f"📚 Today's Class: {course}")
            
            students_query = """
            SELECT DISTINCT s.* FROM students s 
            JOIN enrollments e ON s.id = e.student_id 
            WHERE e.course_id = %s ORDER BY s.roll_no
            """
            students_df = pd.read_sql(students_query, conn, params=[int(course_id)])
            students_df = students_df.drop_duplicates(subset=['id'])
            
            if not students_df.empty:
                st.subheader(f"Students in {course} ({len(students_df)} students)")
                
                attendance_data = []
                for idx, student in students_df.iterrows():
                    col1, col2 = st.columns([2, 1])
                    col1.write(f"{student['roll_no']} - {student['full_name']}")
                    status = col2.selectbox("Status", ["Select Status", "PRESENT", "ABSENT", "LATE", "EXCUSED"],
                        key=f"attendance_{course_id}_{student['id']}_{idx}")
                    if status != "Select Status":
                        attendance_data.append({'student_id': student['id'], 'status': status})
                
                if st.button("📝 Submit Attendance", type="primary"):
                    if attendance_data:
                        submit_attendance(attendance_data, course_id, class_date, class_time)
                    else:
                        st.warning("Please select status for students")
            else:
                st.info("No students enrolled in this course")
        else:
            st.info("No courses available")

def submit_attendance(attendance_data, course_id, class_date, class_time):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            success_count = 0
            for record in attendance_data:
                cur.execute(
                    "SELECT COUNT(*) FROM attendance WHERE student_id = %s AND course_id = %s AND date = %s",
                    (int(record['student_id']), int(course_id), class_date))
                if cur.fetchone()[0] == 0:
                    cur.execute(
                        "INSERT INTO attendance (student_id, course_id, date, status, taken_by_user_id, taken_at) VALUES (%s, %s, %s, %s, %s, %s)",
                        (int(record['student_id']), int(course_id), class_date, record['status'].lower(), 
                         int(st.session_state.user_id), f"{class_date} {class_time}"))
                    success_count += 1
            conn.commit()
            if success_count > 0:
                st.toast(f"✅ Attendance marked for {success_count} students!", icon="✅")
                st.balloons()
            else:
                st.toast("⚠️ Attendance already marked!", icon="⚠️")
    except Exception as e:
        st.toast(f"❌ Error: {str(e)[:30]}...", icon="❌")

def render_view_records():
    st.subheader("📊 Attendance Records")
    col1, col2 = st.columns(2)
    start_date = col1.date_input("From Date", value=date.today() - timedelta(days=7))
    end_date = col2.date_input("To Date", value=date.today())
    
    with get_conn() as conn:
        query = """
        SELECT s.roll_no, s.full_name, c.name as course, a.status, a.date
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        JOIN courses c ON a.course_id = c.id
        WHERE a.date BETWEEN %s AND %s
        ORDER BY a.date DESC LIMIT 200
        """
        df = pd.read_sql(query, conn, params=[start_date, end_date])
        st.dataframe(df, use_container_width=True)
        
        if not df.empty:
            csv_data = df.to_csv(index=False)
            st.download_button("📄 Download CSV", csv_data, "attendance_report.csv", "text/csv")

def render_edit_attendance():
    st.subheader("✏️ Edit Attendance")
    with get_conn() as conn:
        edit_query = """
        SELECT a.id, s.roll_no, s.full_name, c.name as course, a.status, a.date
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        JOIN courses c ON a.course_id = c.id
        WHERE a.taken_by_user_id = %s AND a.date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        ORDER BY a.date DESC
        """
        edit_df = pd.read_sql(edit_query, conn, params=[st.session_state.user_id])
        
        if not edit_df.empty:
            selected_record = st.selectbox("Select Record to Edit",
                edit_df.apply(lambda x: f"{x['roll_no']} - {x['course']} - {x['date']}", axis=1))
            
            if selected_record:
                record_idx = edit_df.index[edit_df.apply(lambda x: f"{x['roll_no']} - {x['course']} - {x['date']}", axis=1) == selected_record][0]
                record = edit_df.iloc[record_idx]
                
                col1, col2 = st.columns(2)
                new_status = col1.selectbox("New Status", ["PRESENT", "ABSENT", "LATE", "EXCUSED"])
                justification = col2.text_area("Justification (Required)")
                
                if st.button("💾 Update Attendance") and justification:
                    submit_edit_request(record, new_status, justification)

def submit_edit_request(record, new_status, justification):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO pending_edits (attendance_id, old_status, new_status, faculty_id, justification) VALUES (%s, %s, %s, %s, %s)",
                (int(record['id']), record['status'], new_status, st.session_state.user_id, justification))
            conn.commit()
            st.toast("📝 Edit request submitted for admin approval", icon="📝")
    except Exception as e:
        st.toast(f"❌ Error: {str(e)[:30]}...", icon="❌")

def render_reports():
    st.subheader("📋 Attendance Status Reports")
    with get_conn() as conn:
        col1, col2, col3 = st.columns(3)
        
        total_query = "SELECT COUNT(DISTINCT CONCAT(date, '_', TIME_FORMAT(taken_at, '%H:%i'))) as total_days FROM attendance WHERE taken_by_user_id = %s"
        total_df = pd.read_sql(total_query, conn, params=[st.session_state.user_id])
        col1.metric("Classes Conducted", total_df.iloc[0]['total_days'] if not total_df.empty else 0)
        
        students_query = "SELECT COUNT(DISTINCT s.id) as total_students FROM students s JOIN enrollments e ON s.id = e.student_id"
        students_df = pd.read_sql(students_query, conn)
        col2.metric("Total Students", students_df.iloc[0]['total_students'] if not students_df.empty else 0)
        
        pending_query = "SELECT COUNT(*) as pending FROM pending_edits WHERE faculty_id = %s AND status = 'pending'"
        pending_df = pd.read_sql(pending_query, conn, params=[st.session_state.user_id])
        col3.metric("Pending Edits", pending_df.iloc[0]['pending'] if not pending_df.empty else 0)
        
        st.subheader("📚 Course-wise Summary")
        summary_query = """
        SELECT c.name as course,
               COUNT(DISTINCT CONCAT(a.date, '_', TIME_FORMAT(a.taken_at, '%H:%i'))) as classes_held,
               COUNT(a.id) as total_records,
               SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as present_count,
               ROUND(SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.id), 2) as avg_attendance
        FROM courses c
        LEFT JOIN attendance a ON c.id = a.course_id
        WHERE a.taken_by_user_id = %s
        GROUP BY c.id
        ORDER BY c.name
        """
        summary_df = pd.read_sql(summary_query, conn, params=[st.session_state.user_id])
        
        if not summary_df.empty:
            st.dataframe(summary_df, use_container_width=True)
        else:
            st.info("No attendance data available")
