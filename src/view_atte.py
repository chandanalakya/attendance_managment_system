# streamlit_app.py
# Student Attendance viewer + CSV/PDF download

import sqlite3
import pandas as pd
import io
import streamlit as st
from typing import List, Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pathlib import Path

# ---------------------- Database setup ----------------------

# Automatically locate DB in the same folder as this script
BASE_DIR = Path(__file__).resolve().parent
DB_FILENAME = "view_attendance.db"
DB_PATH = BASE_DIR / DB_FILENAME

def get_connection(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    db_str = str(db_path)
    conn = sqlite3.connect(db_str)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------- Debug Info (temporary) ----------------------
try:
    conn_test = get_connection()
    cur = conn_test.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    print("DEBUG: Using DB path:", str(DB_PATH))
    print("DEBUG: Tables in DB at startup:", tables)
    conn_test.close()
except Exception as e:
    print("DEBUG: Error while checking DB:", e)

# ---------------------- Database helpers ----------------------

def get_subjects(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM subjects ORDER BY name")
    return [dict(row) for row in cur.fetchall()]

def get_student_by_roll(conn: sqlite3.Connection, roll_no: str) -> Dict[str, Any]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE roll_no = ?", (roll_no,))
    row = cur.fetchone()
    return dict(row) if row else None

def get_attendance_by_subject(conn: sqlite3.Connection, student_id: int, subject_id: int) -> pd.DataFrame:
    query = """
    SELECT a.date AS date, s.name AS subject, a.status AS status
    FROM attendance a
    JOIN subjects s ON s.id = a.subject_id
    WHERE a.student_id = ? AND a.subject_id = ?
    ORDER BY a.date DESC
    """
    df = pd.read_sql_query(query, conn, params=(student_id, subject_id))
    return df

# ---------------------- Export helpers ----------------------

def generate_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")

def generate_pdf_bytes(df: pd.DataFrame, title: str = "Attendance Report") -> bytes:
    buf = io.BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    x_margin = 40
    y = height - 60

    p.setFont("Helvetica-Bold", 14)
    p.drawString(x_margin, y, title)
    y -= 25

    p.setFont("Helvetica", 10)
    cols = list(df.columns)
    col_x = [x_margin + i * 150 for i in range(len(cols))]

    for i, col in enumerate(cols):
        p.drawString(col_x[i], y, str(col))
    y -= 18

    for _, row in df.iterrows():
        if y < 50:
            p.showPage()
            y = height - 60
            p.setFont("Helvetica", 10)
        for i, col in enumerate(cols):
            p.drawString(col_x[i], y, str(row[col]))
        y -= 16

    p.save()
    buf.seek(0)
    return buf.read()

# ---------------------- Streamlit UI ----------------------

st.set_page_config(page_title="Student Attendance", layout="centered")
st.title("Student Attendance Viewer")

with st.form("login_form"):
    roll_no = st.text_input("Enter your roll number", value="21CSE001")
    submitted = st.form_submit_button("View Attendance")

if submitted:
    conn = get_connection()
    student = get_student_by_roll(conn, roll_no)
    if not student:
        st.error("Student not found. Please check your roll number.")
    else:
        st.success(f"Welcome {student['name']} (Roll: {student['roll_no']})")
        subjects = get_subjects(conn)
        subj_options = {s['name']: s['id'] for s in subjects}

        subject_choice = st.selectbox("Select subject", options=list(subj_options.keys()))
        subject_id = subj_options[subject_choice]

        df = get_attendance_by_subject(conn, student['id'], subject_id)
        if df.empty:
            st.info("No attendance records for this subject.")
        else:
            st.dataframe(df)

            csv_bytes = generate_csv_bytes(df)
            pdf_bytes = generate_pdf_bytes(df, title=f"Attendance - {subject_choice}")

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download CSV",
                    data=csv_bytes,
                    file_name=f"attendance_{student['roll_no']}_{subject_choice}.csv",
                    mime="text/csv",
                )
            with col2:
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name=f"attendance_{student['roll_no']}_{subject_choice}.pdf",
                    mime="application/pdf",
                )

        conn.close()
