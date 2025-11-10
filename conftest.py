import os
import pytest
import mysql.connector
from dotenv import load_dotenv

# Load .env if exists
load_dotenv()

# Default test database settings
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "127.0.0.1")
TEST_DB_PORT = int(os.getenv("TEST_DB_PORT", 3307))
TEST_DB_USER = os.getenv("TEST_DB_USER", "root")
TEST_DB_PASS = os.getenv("TEST_DB_PASS", "pass")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "sams_db")

@pytest.fixture(scope="session")
def test_db_conn():
    """Provides a reusable DB connection for integration tests."""
    conn = mysql.connector.connect(
        host=TEST_DB_HOST,
        port=TEST_DB_PORT,
        user=TEST_DB_USER,
        password=TEST_DB_PASS,
        database=TEST_DB_NAME,
        auth_plugin="mysql_native_password"
    )
    yield conn
    conn.close()
