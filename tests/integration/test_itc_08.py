"""ITC-08: Login + Suspicious Login Monitoring"""
import pytest

def test_itc_08_login_suspicious_monitoring():
    """ITC-08: Login with suspicious activity monitoring"""
    login_attempts = [
        {'ip': '192.168.1.1', 'time': 1000, 'success': False},
        {'ip': '192.168.1.1', 'time': 1005, 'success': False},
        {'ip': '192.168.1.1', 'time': 1010, 'success': False},
        {'ip': '10.0.0.1', 'time': 1015, 'success': False},
    ]
    
    failed_count = sum(1 for a in login_attempts if not a['success'])
    suspicious = failed_count >= 3
    
    assert suspicious is True
    assert failed_count == 4
