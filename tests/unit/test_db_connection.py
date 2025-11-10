import mysql.connector
import pytest

def test_mysql_connection(monkeypatch):
    """✅ Check if MySQL connection parameters are valid."""
    def mock_connect(**kwargs):
        assert kwargs["host"] == "localhost"
        assert kwargs["user"] == "root"
        assert kwargs["database"] == "facAdm"
        return True

    monkeypatch.setattr(mysql.connector, "connect", mock_connect)
    result = mysql.connector.connect(
        host="localhost", user="root", password="Lakshmireddy@1", database="facAdm"
    )
    assert result is True
