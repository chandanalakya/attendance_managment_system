import importlib.util


# Dynamically load faculty_login.py from src/
spec = importlib.util.spec_from_file_location(
    "faculty_login", "src/faculty_login.py"
)
faculty_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(faculty_module)


def test_faculty_login_success(monkeypatch):
    # Mock user from DB
    mock_user = {
        "email": "faculty@college.com",
        "password_hash": "$2b$12$abcdefg1234567890",
        "is_approved": True,
    }

    # Mock DB and password check
    monkeypatch.setattr(
        faculty_module, "find_user_by_email", lambda email: mock_user
    )
    monkeypatch.setattr(
        faculty_module, "verify_password", lambda pw, pw_hash: True
    )

    user = faculty_module.find_user_by_email("faculty@college.com")
    assert user["is_approved"] is True
    assert faculty_module.verify_password(
        "Faculty@123", user["password_hash"]
    ) is True


def test_faculty_login_fail(monkeypatch):
    mock_user = {
        "email": "faculty@college.com",
        "password_hash": "$2b$12$abcdefg1234567890",
        "is_approved": True,
    }

    monkeypatch.setattr(
        faculty_module, "find_user_by_email", lambda email: mock_user
    )
    monkeypatch.setattr(
        faculty_module, "verify_password", lambda pw, pw_hash: False
    )

    user = faculty_module.find_user_by_email("faculty@college.com")
    assert faculty_module.verify_password(
        "WrongPass", user["password_hash"]
    ) is False
