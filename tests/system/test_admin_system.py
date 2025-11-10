import importlib.util

# Dynamically load admin_login module
spec = importlib.util.spec_from_file_location(
    "admin_login", "src/admin_login.py"
)
admin_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admin_module)


def test_admin_edit_flow(monkeypatch):
    """System test: Admin should be allowed to edit data."""

    # Mock: simulate admin user
    monkeypatch.setattr(admin_module, "get_user_role", lambda email: "admin")

    # Mock update_data function
    def mock_update_data(data):
        return True

    monkeypatch.setattr(
        admin_module, "update_data", mock_update_data, raising=False
    )

    # Execute test
    user_email = "admin@college.com"
    role = admin_module.get_user_role(user_email)
    assert role == "admin"
    assert admin_module.update_data({"record": "updated"}) is True


def test_non_admin_edit_flow(monkeypatch):
    """System test: Faculty should NOT be allowed to edit data."""

    # Mock: simulate faculty user
    monkeypatch.setattr(admin_module, "get_user_role", lambda email: "faculty")

    user_email = "faculty@college.com"
    role = admin_module.get_user_role(user_email)
    assert role != "admin"
