import mysql.connector
from unittest.mock import patch
from src.login_system import get_connection

def test_get_connection(monkeypatch):
    """✅ Ensure get_connection() calls mysql.connector.connect() properly."""
    called = {}

    def mock_connect(**kwargs):
        called["used"] = True
        return "mock_connection"

    monkeypatch.setattr(mysql.connector, "connect", mock_connect)
    conn = get_connection()
    assert conn == "mock_connection"
    assert "used" in called
