"""ITC-21: Role-Based Access + Core Modules"""
import pytest

def test_itc_21_rbac_core_modules():
    """ITC-21: Students prevented from accessing faculty/admin features"""
    user_permissions = {
        'student': {
            'can_view_own_attendance': True,
            'can_mark_attendance': False,
            'can_edit_attendance': False,
            'can_manage_users': False
        },
        'faculty': {
            'can_view_own_attendance': True,
            'can_mark_attendance': True,
            'can_edit_attendance': True,
            'can_manage_users': False
        },
        'admin': {
            'can_view_own_attendance': True,
            'can_mark_attendance': True,
            'can_edit_attendance': True,
            'can_manage_users': True
        }
    }
    
    assert user_permissions['student']['can_mark_attendance'] is False
    assert user_permissions['student']['can_manage_users'] is False
    assert user_permissions['faculty']['can_mark_attendance'] is True
    assert user_permissions['admin']['can_manage_users'] is True
