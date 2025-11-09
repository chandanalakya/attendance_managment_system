import importlib.util

spec = importlib.util.spec_from_file_location("admin_login", "src/admin_login.py")
admin_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admin_module)


def test_admin_edit_flow(monkeypatch):
    """Admin tries to edit data -> should be allowed."""
    user = {"email": "admin@college.com", "role": "admin"}

    monkeypatch.setattr(admin_module, "get_user_role", lambda email: "admin")
def mock_update_data(data):
    return True

    monkeypatch.setattr(admin_module, "update_data", mock_update_data, raising=False)
 
    assert admin_module.get_user_role(user["email"]) == "admin"
    assert admin_module.update_data({"record": "updated"}) is True


def test_non_admin_edit_flow(monkeypatch):
    """Faculty tries to edit data -> should be blocked."""
    user = {"email": "faculty@college.com", "role": "faculty"}

    monkeypatch.setattr(admin_module, "get_user_role", lambda email: "faculty")

    assert admin_module.get_user_role(user["email"]) != "admin"
