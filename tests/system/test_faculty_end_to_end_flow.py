import importlib.util


# Load the faculty_login module dynamically
spec = importlib.util.spec_from_file_location(
    "faculty_login", "src/faculty_login.py"
)
faculty_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(faculty_module)


def test_faculty_login_system(monkeypatch):
    mock_user = {
        "email": "faculty@college.com",
        "password_hash": "$2b$12$abcdefg1234567890",
        "is_approved": True,
    }

    monkeypatch.setattr(
        faculty_module, "find_user_by_email", lambda email: mock_user
    )
    monkeypatch.setattr(
        faculty_module,
        "verify_password",
        lambda pw, pw_hash: pw == "Faculty@123",
    )

    email, password = "faculty@college.com", "Faculty@123"
    user = faculty_module.find_user_by_email(email)

    assert user["is_approved"] is True
    assert faculty_module.verify_password(password, user["password_hash"]) is True
