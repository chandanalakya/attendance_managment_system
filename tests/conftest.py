"""Pytest Configuration and Fixtures"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(autouse=True)
def mock_streamlit():
    """Auto-mock streamlit for all tests"""
    with patch('streamlit.session_state', Mock()) as mock_st:
        mock_st.authenticated = False
        mock_st.user_role = None
        mock_st.user_id = None
        mock_st.username = None
        mock_st.failed_attempts = 0
        mock_st.locked_until = None
        yield mock_st

@pytest.fixture
def mock_db_connection():
    """Mock database connection"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None
    return mock_conn, mock_cursor

@pytest.fixture
def sample_user():
    """Sample user data"""
    return {
        'id': 1,
        'username': 'testuser',
        'role': 'student',
        'email': 'test@test.com',
        'full_name': 'Test User'
    }

@pytest.fixture
def sample_attendance():
    """Sample attendance data"""
    return {
        'id': 1,
        'student_id': 1,
        'course_id': 1,
        'date': '2024-01-01',
        'status': 'present'
    }
