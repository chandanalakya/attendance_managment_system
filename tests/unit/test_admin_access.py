import src.admin_login as admin_module


# --- Mocked role logic for tests ---
def mock_get_user_role(email):
    if "admin" in email:
        return "admin"
    elif "faculty" in email:
        return "faculty"
    else:
        return "student"


def can_edit_data(email):
    """Returns True if the user is an admin."""
    return mock_get_user_role(email) == "admin"


# -----------------------------
# UNIT TESTS
# -----------------------------
def test_admin_can_edit():
    assert can_edit_data("admin@college.com") is True


def test_student_cannot_edit():
    assert can_edit_data("student@college.com") is False


def test_faculty_cannot_edit():
    assert can_edit_data("faculty@college.com") is False


def test_admin_module_has_login_user_function():
    """Check that login_user function exists in admin_module."""
    assert hasattr(
        admin_module,
        "login_user"
    )


def test_admin_module_login_user(monkeypatch):
    """Functional test for login_user with mocked DB and password."""

    # Mock find_user_by_email
    monkeypatch.setattr(
        admin_module,
        "find_user_by_email",
        lambda email: {
            "email": email,
            "password_hash": "fakehash",
            "role": "admin",
            "is_approved": True
        }
    )

    # Mock verify_password
    monkeypatch.setattr(
        admin_module,
        "verify_password",
        lambda pw, pw_hash: True
    )

    ok, user = admin_module.login_user("admin@college.com", "password")
    assert ok is True
    assert user["role"] == "admin"
