import os
import mysql.connector
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------------------------
# ✅ DATABASE CONNECTION SETUP
# -------------------------------------------------------------------

# MySQL Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Rohan@200525'),
    'database': os.getenv('DB_NAME', 'sams2'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'autocommit': True
}

DATABASE_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False
)

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def get_db():
    """Provide a transactional session scope for ORM operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """
    Test MySQL database connection.
    Returns (success: bool, message: str)
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return True, "Database connection successful"
    except mysql.connector.Error as e:
        return False, f"Database connection failed: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

@contextmanager
def get_conn():
    """
    Provide a context-managed MySQL connection.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        yield conn
    except mysql.connector.Error as e:
        raise ConnectionError(f"Database connection failed: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()


def init_db(schema_file=None):
    """
    Initialize the MySQL database.
    """
    if schema_file and os.path.exists(schema_file):
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_sql = f.read()
    elif os.path.exists("database/sams2_complete.sql"):
        with open("database/sams2_complete.sql", "r", encoding="utf-8") as f:
            schema_sql = f.read()
    else:
        # Default MySQL schema
        schema_sql = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    roll_no VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    student_id INT NOT NULL,
    status ENUM('PRESENT','ABSENT','LATE','EXCUSED') NOT NULL,
    taken_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    taken_by_user_id INT,
    notes TEXT,
    FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(taken_by_user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action_type ENUM('ADD','EDIT','DELETE','LOG_MOD_ATTEMPT') NOT NULL,
    attendance_id INT,
    user_id INT,
    ip_address VARCHAR(45),
    details TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(attendance_id) REFERENCES attendance(id) ON DELETE SET NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS audit_security_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    user_id INT,
    ip_address VARCHAR(45),
    target_table VARCHAR(100),
    operation VARCHAR(50),
    details TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);
"""

    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            # Execute each statement separately
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            for statement in statements:
                cursor.execute(statement)
            conn.commit()
            cursor.close()
        print("MySQL database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise