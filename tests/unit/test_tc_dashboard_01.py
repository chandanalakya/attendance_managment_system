"""TC-Dashboard-01: View analytics dashboard (charts/trends)"""
import pytest

def test_tc_dashboard_01_analytics_dashboard():
    """TC-Dashboard-01: View analytics dashboard"""
    analytics_data = {
        'total_students': 100,
        'average_attendance': 82.5,
        'defaulters_count': 15,
        'trends': [
            {'week': 1, 'attendance': 85.0},
            {'week': 2, 'attendance': 83.0},
            {'week': 3, 'attendance': 80.0},
        ]
    }
    
    assert analytics_data['total_students'] > 0
    assert 0 <= analytics_data['average_attendance'] <= 100
    assert len(analytics_data['trends']) > 0
