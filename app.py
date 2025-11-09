
import os
import pandas as pd
import streamlit as st
from src.utils.db import get_conn, init_db, DB_PATH
from src.models.attendance import add_attendance, edit_attendance, delete_attendance, attempt_modify_audit_logs
from src.models.audit_log import fetch_logs
from src.utils.export_csv import to_csv_bytes
from src.utils.export_pdf import to_pdf_bytes

st.set_page_config(page_title="SAMS2 - Attendance & Audit Logs", layout="wide")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")
if not os.path.exists(os.path.join(os.path.dirname(__file__), "sams2.db")):
    init_db(SCHEMA_PATH)

st.title("SAMS2 - Attendance Audit Logging")

with st.sidebar:
    st.header("Quick Demo Inputs")
    ip = st.text_input("Your IP address", value="127.0.0.1")
    user_id = st.number_input("Acting user_id", value=1, step=1)
    st.markdown("This demo uses a local SQLite DB at: `" + DB_PATH + "`.")

tab1, tab2 = st.tabs(["Attendance Actions (Demo)", "Audit Log Viewer"])

with tab1:
    st.subheader("Add/Edit/Delete Attendance (Demo)")
    course_id = st.number_input("Course ID", value=1, step=1)
    student_id = st.number_input("Student ID", value=1, step=1)
    status = st.selectbox("Status", ["PRESENT","ABSENT","LATE","EXCUSED"])
    notes = st.text_input("Notes", value="")

    colA, colB, colC = st.columns(3)
    with get_conn() as conn:
        if colA.button("Add Attendance"):
            att_id = add_attendance(conn, course_id=course_id, student_id=student_id, status=status, taken_by_user_id=int(user_id), ip_address=ip, notes=notes)
            st.success(f"Added attendance id={att_id}. Logged ADD.")
        att_id_for_edit = colB.number_input("Attendance ID to Edit/Delete", value=1, step=1)
        if colB.button("Edit Attendance"):
            edit_attendance(conn, attendance_id=int(att_id_for_edit), new_status=status, user_id=int(user_id), ip_address=ip, notes=notes)
            st.success(f"Edited attendance id={int(att_id_for_edit)}. Logged EDIT.")
        if colC.button("Delete Attendance"):
            delete_attendance(conn, attendance_id=int(att_id_for_edit), user_id=int(user_id), ip_address=ip)
            st.success(f"Deleted attendance id={int(att_id_for_edit)}. Logged DELETE.")

    st.divider()
    st.subheader("Tamper Attempt (blocked & logged)")
    colU, colD = st.columns(2)
    with get_conn() as conn:
        if colU.button("Attempt UPDATE audit_logs"):
            try:
                attempt_modify_audit_logs(conn, operation="UPDATE", user_id=int(user_id), ip_address=ip)
            except Exception as e:
                st.error(f"Blocked: {e}")
        if colD.button("Attempt DELETE audit_logs"):
            try:
                attempt_modify_audit_logs(conn, operation="DELETE", user_id=int(user_id), ip_address=ip)
            except Exception as e:
                st.error(f"Blocked: {e}")

with tab2:
    st.subheader("Audit Log Viewer")
    c1, c2, c3, c4 = st.columns(4)
    start = c1.date_input("Start date", value=None)
    end = c2.date_input("End date", value=None)
    filter_user = c3.text_input("User ID filter", value="")
    filter_course = c4.text_input("Course ID filter", value="")

    start_str = start.isoformat() if start else None
    end_str = None
    if end:
        end_str = pd.to_datetime(end).to_pydatetime().replace(hour=23, minute=59, second=59).isoformat()
    user_filter_val = int(filter_user) if filter_user.strip().isdigit() else None
    course_filter_val = int(filter_course) if filter_course.strip().isdigit() else None

    with get_conn() as conn:
        rows = fetch_logs(conn, start=start_str, end=end_str, user_id=user_filter_val, course_id=course_filter_val)

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    col1, col2 = st.columns(2)
    if col1.download_button("Export CSV", data=to_csv_bytes(rows), file_name="audit_logs.csv", mime="text/csv"):
        st.toast("CSV exported.")
    if col2.download_button("Export PDF", data=to_pdf_bytes("SAMS2 Audit Logs", rows), file_name="audit_logs.pdf", mime="application/pdf"):
        st.toast("PDF exported.")
