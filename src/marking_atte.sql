-- Create Students table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
);

-- Create Subjects table
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- Create Attendance table
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(subject_id) REFERENCES subjects(id)
);

-- Sample Students
INSERT OR IGNORE INTO students (roll, name) VALUES
('21CSE001', 'Chitra Madarakhandi'),
('21CSE002', 'Rahul Kumar'),
('21CSE003', 'Ananya Rao');

-- Sample Subjects
INSERT OR IGNORE INTO subjects (name) VALUES
('Mathematics'),
('Physics'),
('Computer Science');
