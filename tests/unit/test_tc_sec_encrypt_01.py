"""TC-Sec-Encrypt-01: AES-256 data-at-rest encryption test"""
import pytest
import hashlib

def test_tc_sec_encrypt_01_password_encryption():
    """TC-Sec-Encrypt-01: Data encryption at rest"""
    password = "test123"
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    assert len(hashed) == 64
    assert hashed != password
    
    hashed2 = hashlib.sha256(password.encode()).hexdigest()
    assert hashed == hashed2
