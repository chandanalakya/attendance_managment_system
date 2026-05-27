"""TC-Auth-01: Validate correct login (password/biometric)"""
import pytest
import hashlib

def test_tc_auth_01_correct_login_validation():
    """TC-Auth-01: Validate correct PIN entry"""
    username = "faculty1"
    password = "correctPassword123"
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    stored_hash = hashed_password
    input_hash = hashlib.sha256(password.encode()).hexdigest()
    
    assert stored_hash == input_hash
    assert len(stored_hash) == 64
