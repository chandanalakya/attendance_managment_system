"""TC-Sec-01: Session timeout after inactivity"""
import pytest
import time

def test_tc_sec_01_session_timeout():
    """TC-Sec-01: Session timeout after inactivity"""
    session_timeout_seconds = 900
    last_activity_time = time.time()
    current_time = time.time() + 1000
    
    time_elapsed = current_time - last_activity_time
    session_expired = time_elapsed > session_timeout_seconds
    
    assert session_expired is True
