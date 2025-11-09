from src.login_system import setup_database

def test_setup_database(monkeypatch):
    """✅ Ensure setup_database executes without DB errors."""
    called = {}

    class MockCursor:
        def execute(self, *a, **k): called["execute"] = True
        def fetchone(self): return [0]
        def executemany(self, *a, **k): called["executemany"] = True
        def close(self): pass

    class MockConn:
        def cursor(self): return MockCursor()
        def commit(self): called["commit"] = True
        def close(self): called["close"] = True

    monkeypatch.setattr("src.login_system.get_connection", lambda: MockConn())
    setup_database()
    assert "execute" in called
    assert "commit" in called
    assert "close" in called
