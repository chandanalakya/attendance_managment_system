import os
import pytest
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv

# Load .env if exists
load_dotenv()

# Default test database settings
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "127.0.0.1")
TEST_DB_PORT = int(os.getenv("TEST_DB_PORT", 3306))  # default MySQL port
TEST_DB_USER = os.getenv("TEST_DB_USER", "root")
TEST_DB_PASS = os.getenv("TEST_DB_PASS", "pass")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "sams_db")


@pytest.fixture(scope="session")
def test_db_conn():
    """
    Provides a reusable MySQL DB connection for integration tests.
    Creates the database if it doesn't exist.
    """
    try:
        # Connect without specifying database first
        conn = mysql.connector.connect(
            host=TEST_DB_HOST,
            port=TEST_DB_PORT,
            user=TEST_DB_USER,
            password=TEST_DB_PASS,
            auth_plugin="mysql_native_password"
        )
        cursor = conn.cursor()
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{TEST_DB_NAME}`;")
        conn.database = TEST_DB_NAME

        yield conn

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            pytest.fail("MySQL access denied: check username/password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            pytest.fail(f"MySQL database {TEST_DB_NAME} does not exist and could not be created")
        else:
            pytest.fail(f"MySQL connection error: {err}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
