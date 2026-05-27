"""Coverage tests for db module"""
import pytest
from unittest.mock import patch, Mock, MagicMock
import mysql.connector
from src.utils.db import test_connection, get_conn, init_db

@patch('mysql.connector.connect')
def test_test_connection_success(mock_connect):
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    
    success, message = test_connection()
    assert success is True
    assert "successful" in message.lower()

@patch('mysql.connector.connect')
def test_test_connection_failure(mock_connect):
    mock_connect.side_effect = mysql.connector.Error("Connection failed")
    
    success, message = test_connection()
    assert success is False
    assert "failed" in message.lower()

@patch('mysql.connector.connect')
def test_test_connection_unexpected_error(mock_connect):
    mock_connect.side_effect = Exception("Unexpected")
    
    success, message = test_connection()
    assert success is False
    assert "Unexpected" in message

@patch('mysql.connector.connect')
def test_get_conn_success(mock_connect):
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True
    mock_connect.return_value = mock_conn
    
    with get_conn() as conn:
        assert conn is not None

@patch('mysql.connector.connect')
def test_get_conn_failure(mock_connect):
    mock_connect.side_effect = mysql.connector.Error("Connection failed")
    
    with pytest.raises(ConnectionError):
        with get_conn() as conn:
            pass

@patch('src.utils.db.get_conn')
def test_init_db_with_schema_file(mock_conn):
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.cursor.return_value = mock_cursor
    mock_db.__enter__.return_value = mock_db
    mock_db.__exit__.return_value = None
    mock_conn.return_value.__enter__.return_value = mock_db
    mock_conn.return_value.__exit__.return_value = None
    
    init_db()
    assert mock_cursor.execute.called

@patch('src.utils.db.get_conn')
def test_init_db_exception(mock_conn):
    mock_conn.side_effect = Exception("DB Error")
    
    with pytest.raises(Exception):
        init_db()
