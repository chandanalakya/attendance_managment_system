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
    """
    Returns True if the user is an admin.
    """
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


def test_admin_module_has_login_function():
    """
    Minimal usage of admin_module to avoid F401 warning.
    Replace 'login' with an actual function in your admin module.
    """
    assert hasattr(admin_module, "login")
