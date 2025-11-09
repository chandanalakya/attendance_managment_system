import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Attendance Dashboard", layout="wide")


# ---------- DATABASE CONNECTION ----------
@st.cache_data
def load_data():
    """Load attendance data from the facAdm database using SQLAlchemy."""
    try:
        engine = create_engine("mysql+mysqlconnector://root:Lakshmireddy@1@localhost/facAdm")

        query = """
        SELECT student_id, student_name, course, faculty, attendance_percentage
        FROM attendance
        """

        with engine.connect() as conn:
            df = pd.read_sql(query, conn)

        return df

    except SQLAlchemyError as e:
        st.error(f"❌ Database connection error: {e}")
        return pd.DataFrame()


# ---------- LOAD DATA ----------
df = load_data()

st.title("🎓 Student Attendance Management Dashboard")

if df.empty:
    st.warning("No data available. Please check the database connection or data.")
else:
    # ---------- ROLE SELECTION ----------
    role = st.sidebar.radio("Select Role:", ["Faculty", "Admin"])

    # ---------- FACULTY DASHBOARD ----------
    if role == "Faculty":
        st.subheader("👩‍🏫 Faculty Dashboard")

        faculty_list = df["faculty"].dropna().unique()
        if len(faculty_list) == 0:
            st.info("No faculty data available.")
        else:
            faculty_name = st.sidebar.selectbox("Select Your Name:", faculty_list)
            faculty_courses = df[df["faculty"] == faculty_name]["course"].unique()

            if len(faculty_courses) == 0:
                st.info("No courses found for this faculty.")
            else:
                selected_course = st.sidebar.selectbox("Select a Course You Handle:", faculty_courses)

                faculty_data = df[
                    (df["faculty"] == faculty_name) &
                    (df["course"] == selected_course)
                ]

                st.write(f"### Students in {selected_course} (Handled by {faculty_name})")
                st.dataframe(
                    faculty_data[["student_id", "student_name", "attendance_percentage"]]
                    .sort_values(by="student_id")
                    .reset_index(drop=True)
                )

    # ---------- ADMIN DASHBOARD ----------
    elif role == "Admin":
        st.subheader("🧑‍💼 Admin Dashboard")

        course_list = df["course"].dropna().unique()
        if len(course_list) == 0:
            st.info("No courses found.")
        else:
            selected_course = st.sidebar.selectbox("Select Course to Review:", course_list)

            low_attendance = df[
                (df["course"] == selected_course) &
                (df["attendance_percentage"] < 75)
            ]

            if low_attendance.empty:
                st.success(f"✅ All students in {selected_course} have ≥ 75% attendance.")
            else:
                st.error(f"⚠️ Students below 75% in {selected_course}:")
                st.dataframe(
                    low_attendance[["student_id", "student_name", "attendance_percentage"]]
                    .sort_values(by="attendance_percentage")
                    .reset_index(drop=True)
                )
