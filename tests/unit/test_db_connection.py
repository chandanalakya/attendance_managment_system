from src.faculty_attendance import get_connection

def test_get_connection(monkeypatch):
    """Ensure get_connection uses mysql.connector.connect correctly."""
    called = {}

    def mock_connect(**kwargs):
        called["used"] = True
        return "mock_connection"

    # ✅ Patch inside the module where it's used
    monkeypatch.setattr("src.faculty_attendance.mysql.connector.connect", mock_connect)

    conn = get_connection()
    assert conn == "mock_connection"
    assert called.get("used", False)
