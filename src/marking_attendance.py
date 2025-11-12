import streamlit as st
import sqlite3
from datetime import date
import pandas as pd

DB_PATH = "marking_atte.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def mark_attendance(roll, subject_id, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM students WHERE roll=?", (roll,))
    student = cur.fetchone()
    if not student:
        conn.close()
        return False
    student_id = student["id"]
    today = date.today().isoformat()
    cur.execute("INSERT INTO attendance (student_id, subject_id, date, status) VALUES (?, ?, ?, ?)",
                (student_id, subject_id, today, status))
    conn.commit()
    conn.close()
    return True

def get_attendance():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT a.id, s.roll, s.name, sub.name AS subject, a.date, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        JOIN subjects sub ON a.subject_id = sub.id
    """, conn)
    conn.close()
    return df

st.title("Student Attendance Management")

menu = ["Mark Attendance", "View Attendance"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Mark Attendance":
    conn = get_connection()
    students = conn.execute("SELECT roll, name FROM students").fetchall()
    subjects = conn.execute("SELECT id, name FROM subjects").fetchall()
    conn.close()

    student_roll = st.selectbox("Select Student", [f"{s['roll']} - {s['name']}" for s in students])
    subject_choice = st.selectbox("Select Subject", [f"{s['id']} - {s['name']}" for s in subjects])
    status = st.radio("Status", ["Present", "Absent"])

    if st.button("Mark Attendance"):
        roll = student_roll.split(" - ")[0]
        subject_id = int(subject_choice.split(" - ")[0])
        if mark_attendance(roll, subject_id, status):
            st.success(f"Attendance marked for {roll}")
        else:
            st.error("Student not found!")

elif choice == "View Attendance":
    df = get_attendance()
    st.dataframe(df)
