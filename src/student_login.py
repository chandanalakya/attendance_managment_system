import os
import sqlite3
import mysql.connector
import streamlit as st

USE_SQLITE = os.environ.get("USE_SQLITE", "0") == "1"
DB_PATH = os.environ.get("ATTENDANCE_DB", ":memory:")

def get_db_conn():
    """
    Returns a database connection.
    - MySQL for production (default)
    - SQLite in-memory for testing
    """
    if USE_SQLITE:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", "Aazz123@@"),
            database=os.getenv("DB_NAME", "sams_db"),
            auth_plugin="mysql_native_password",
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"❌ Database connection failed: {e}")
        return None
