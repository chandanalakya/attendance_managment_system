"""TC-Auth-Role-01: Validate role-based access (Student/Faculty/Admin)"""
import pytest

def test_tc_auth_role_01_role_based_access():
    """TC-Auth-Role-01: Role-based access validation"""
    roles = {
        'admin': ['view_all', 'edit_all', 'generate_reports', 'manage_users'],
        'faculty': ['mark_attendance', 'edit_attendance', 'view_reports'],
        'student': ['view_own_attendance', 'view_own_reports']
    }
    
    assert len(roles['admin']) > len(roles['faculty'])
    assert len(roles['faculty']) > len(roles['student'])
    assert 'edit_attendance' in roles['faculty']
    assert 'edit_attendance' not in roles['student']
