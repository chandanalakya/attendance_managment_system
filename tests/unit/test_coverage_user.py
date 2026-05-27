"""Coverage tests for user module"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.models.user import init_sample_users

@patch('src.models.user.get_conn')
@patch('src.models.user.st')
def test_init_sample_users_no_users(mock_st, mock_conn):
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [(0,), None, None, (1,)]
    mock_cursor.fetchall.side_effect = [[(1,), (2,)], [(1,), (2,)]]
    mock_db.cursor.return_value = mock_cursor
    mock_db.__enter__.return_value = mock_db
    mock_db.__exit__.return_value = None
    mock_conn.return_value = mock_db
    
    init_sample_users()
    assert mock_cursor.execute.called

@patch('src.models.user.get_conn')
@patch('src.models.user.st')
def test_init_sample_users_with_users(mock_st, mock_conn):
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_db.cursor.return_value = mock_cursor
    mock_db.__enter__.return_value = mock_db
    mock_db.__exit__.return_value = None
    mock_conn.return_value = mock_db
    
    init_sample_users()
    assert mock_cursor.execute.called

@patch('src.models.user.get_conn')
@patch('src.models.user.st')
def test_init_sample_users_exception(mock_st, mock_conn):
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("DB Error")
    mock_db.cursor.return_value = mock_cursor
    mock_db.__enter__.return_value = mock_db
    mock_db.__exit__.return_value = None
    mock_conn.return_value = mock_db
    
    init_sample_users()
    assert mock_cursor.execute.called
