import streamlit as st
import pandas as pd
import mysql.connector
import datetime

# ---------- DATABASE CONNECTION ----------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",                 # your MySQL username
        password="Lakshmireddy@1",   # your MySQL password
        database="attendance_db"
    )

# ---------- FACULTY AUTH ----------
def get_faculty(email, password):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM faculty WHERE email=%s AND password=%s", (email, password))
    faculty = cur.fetchone()
    conn.close()
    return faculty

# ---------- FETCH CLASSES ----------
def get_classes(faculty_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM class WHERE faculty_id=%s", (faculty_id,))
    data = cur.fetchall()
    conn.close()
    return data

# ---------- FETCH STUDENTS ----------
def get_students(class_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM student WHERE class_id=%s", (class_id,))
    data = cur.fetchall()
    conn.close()
    return data

# ---------- MARK ATTENDANCE ----------
def mark_attendance(class_id, attendance_dict, date, start_time, end_time):
    conn = get_connection()
    cur = conn.cursor()
    for sid, present in attendance_dict.items():
        cur.execute("""
            INSERT INTO attendance (student_id, class_id, date, start_time, end_time, present)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE present = VALUES(present)
        """, (sid, class_id, date, start_time, end_time, present))
    conn.commit()
    conn.close()

# ---------- FETCH ATTENDANCE RECORDS ----------
def get_attendance_records(faculty_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT c.name AS class_name, s.roll_number, s.name AS student_name,
               a.date, a.start_time, a.end_time,
               CASE WHEN a.present THEN 'Present' ELSE 'Absent' END AS status
        FROM attendance a
        JOIN student s ON a.student_id = s.id
        JOIN class c ON a.class_id = c.id
        WHERE c.faculty_id = %s
        ORDER BY a.date DESC, a.start_time DESC
    """, (faculty_id,))
    data = cur.fetchall()
    conn.close()
    return data

# ---------- STREAMLIT APP ----------
st.set_page_config(page_title="Faculty Attendance System", layout="wide")
st.title("🎓 Faculty Attendance Management System")

# ---------- LOGIN ----------
st.sidebar.header("Faculty Login")
email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")
login_btn = st.sidebar.button("Login")

if "faculty_id" not in st.session_state:
    st.session_state["faculty_id"] = None

if login_btn:
    faculty = get_faculty(email, password)
    if faculty:
        st.session_state["faculty_id"] = faculty["id"]
        st.session_state["faculty_name"] = faculty["name"]
        st.success(f"Welcome, {faculty['name']} 👋")
    else:
        st.error("Invalid credentials")

# ---------- AFTER LOGIN ----------
if st.session_state["faculty_id"]:
    st.header(f"👨‍🏫 Welcome, {st.session_state['faculty_name']}")
    menu = st.sidebar.radio("Menu", ["Mark Attendance", "View Attendance"])

    # ---------- MARK ATTENDANCE ----------
    if menu == "Mark Attendance":
        classes = get_classes(st.session_state["faculty_id"])
        if not classes:
            st.warning("No classes assigned to you.")
        else:
            class_names = [c["name"] for c in classes]
            selected_class = st.selectbox("Select Class", class_names)
            class_id = [c["id"] for c in classes if c["name"] == selected_class][0]

            # Date & Time selection
            col1, col2, col3 = st.columns(3)
            with col1:
                date = st.date_input("Select Date", datetime.date.today())
            with col2:
                start_time = st.time_input("Start Time", datetime.datetime.now().time())
            with col3:
                end_time = st.time_input("End Time", (datetime.datetime.now() + datetime.timedelta(hours=1)).time())

            # Student List
            students = get_students(class_id)
            if not students:
                st.info("No students in this class yet.")
            else:
                st.subheader(f"Mark Attendance for {selected_class}")
                attendance_dict = {}
                for s in students:
                    attendance_dict[s["id"]] = st.checkbox(f"{s['roll_number']} - {s['name']}", value=True)

                if st.button("Submit Attendance"):
                    mark_attendance(class_id, attendance_dict, date, start_time, end_time)
                    st.success(f"✅ Attendance marked for {selected_class} on {date} ({start_time} - {end_time})")

    # ---------- VIEW ATTENDANCE ----------
    elif menu == "View Attendance":
        st.subheader("📅 Attendance Records")
        records = get_attendance_records(st.session_state["faculty_id"])
        if not records:
            st.info("No attendance records available yet.")
        else:
            df = pd.DataFrame(records)
            st.dataframe(df)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", csv, file_name="attendance_records.csv")
else:
    st.info("Please login to continue.")
