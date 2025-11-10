from src.login_system import hash_password
import hashlib

def test_hash_password():
    """✅ Ensure hashing works with SHA256."""
    password = "mypassword"
    expected = hashlib.sha256(password.encode()).hexdigest()
    assert hash_password(password) == expected
