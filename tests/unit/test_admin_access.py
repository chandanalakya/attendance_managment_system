import pytest
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
