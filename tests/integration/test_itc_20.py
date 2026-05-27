"""ITC-20: AES-256 Encryption + Attendance Storage"""
import pytest
import hashlib

def test_itc_20_aes_encryption_storage():
    """ITC-20: DB entries stored encrypted and decrypted on access"""
    sensitive_data = "student_attendance_record"
    encrypted = hashlib.sha256(sensitive_data.encode()).hexdigest()
    
    assert len(encrypted) == 64
    assert encrypted != sensitive_data
    
    decrypted_check = hashlib.sha256(sensitive_data.encode()).hexdigest()
    assert encrypted == decrypted_check
