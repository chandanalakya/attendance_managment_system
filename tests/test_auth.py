from src.app import create_user, login_user, find_user_by_email

def test_create_and_login_user():
    uid = create_user("Alice","alice@example.com","secret","student")
    assert uid > 0
    found = find_user_by_email("alice@example.com")
    assert found is not None
    assert found["role"] == "student"
    assert login_user("alice@example.com","secret") is not None
    assert login_user("alice@example.com","wrong") is None
