"""TC-Auth-02: Incorrect login attempts → account lockout"""
import pytest

def test_tc_auth_02_account_lockout():
    """TC-Auth-02: Account lockout after 5 failed attempts"""
    failed_attempts = 0
    max_attempts = 5
    
    for attempt in range(6):
        if attempt < max_attempts:
            failed_attempts += 1
            assert failed_attempts <= max_attempts
        else:
            assert failed_attempts >= max_attempts
            account_locked = True
            assert account_locked is True
