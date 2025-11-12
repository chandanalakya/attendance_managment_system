import pytest
from marking_attendance import mark_attendance, get_attendance, get_connection

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    conn = get_connection()
    
    # Create tables if they don't exist
    conn.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll TEXT UNIQUE,
        name TEXT
    )""")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY,
        name TEXT
    )""")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject_id INTEGER,
        date TEXT DEFAULT CURRENT_DATE,
        status TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
    )""")
    
    # Insert sample student and subject
    conn.execute("INSERT OR IGNORE INTO students (roll, name) VALUES ('21CSE001', 'Chitra Madarakhandi')")
    conn.execute("INSERT OR IGNORE INTO subjects (id, name) VALUES (1, 'Mathematics')")
    
    # Clear previous attendance for clean test
    conn.execute("""
    DELETE FROM attendance 
    WHERE student_id = (SELECT id FROM students WHERE roll='21CSE001')
    """)
    
    conn.commit()
    conn.close()

def test_mark_attendance_success():
    result = mark_attendance("21CSE001", 1, "Present")
    assert result is True
    
    df = get_attendance()
    assert not df.empty
    
    last_record = df.iloc[-1]
    assert last_record["roll"] == "21CSE001"
    assert last_record["subject"] == "Mathematics"
    assert last_record["status"] == "Present"

def test_mark_attendance_invalid_student():
    result = mark_attendance("INVALID001", 1, "Absent")
    assert result is False
