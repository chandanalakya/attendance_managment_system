"""Test Runner Script"""
import pytest
import sys

def run_unit_tests():
    """Run unit tests only"""
    return pytest.main(['-v', 'tests/unit', '-m', 'unit or not integration'])

def run_integration_tests():
    """Run integration tests only"""
    return pytest.main(['-v', 'tests/integration', '-m', 'integration'])

def run_all_tests():
    """Run all tests with coverage"""
    return pytest.main([
        '-v',
        'tests/',
        '--cov=src',
        '--cov-report=html',
        '--cov-report=term-missing'
    ])

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'unit':
            sys.exit(run_unit_tests())
        elif sys.argv[1] == 'integration':
            sys.exit(run_integration_tests())
    sys.exit(run_all_tests())
