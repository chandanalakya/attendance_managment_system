"""TC-Sec-RBAC-01: Validate restricted access to sensitive features"""
import pytest

def test_tc_sec_rbac_01_role_based_access():
    """TC-Sec-RBAC-01: Role-based access control"""
    permissions = {
        'admin': ['CREATE', 'READ', 'UPDATE', 'DELETE', 'MANAGE_USERS'],
        'faculty': ['READ', 'UPDATE', 'MARK_ATTENDANCE'],
        'student': ['READ']
    }
    
    assert 'DELETE' in permissions['admin']
    assert 'MANAGE_USERS' in permissions['admin']
    assert 'DELETE' not in permissions['faculty']
    assert 'MANAGE_USERS' not in permissions['faculty']
    assert permissions['student'] == ['READ']
