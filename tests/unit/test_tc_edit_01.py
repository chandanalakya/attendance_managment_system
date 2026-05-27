"""TC-Edit-01: Faculty edits attendance with justification"""
import pytest
from unittest.mock import Mock
from src.models.attendance import edit_attendance

@pytest.fixture
def mock_db():
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn

def test_tc_edit_01_faculty_edits_with_justification(mock_db):
    """TC-Edit-01: Faculty edits attendance with justification"""
    edit_attendance(
        mock_db,
        attendance_id=1,
        new_status="ABSENT",
        user_id=1,
        ip_address="127.0.0.1",
        notes="Student was sick - medical certificate provided"
    )
    
    assert mock_db.commit.called
