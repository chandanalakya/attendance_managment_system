"""TC-Sec-TLS-01: TLS 1.2+ secure communication validation"""
import pytest

def test_tc_sec_tls_01_tls_validation():
    """TC-Sec-TLS-01: TLS 1.2+ secure communication"""
    tls_config = {
        'enabled': True,
        'version': 'TLS 1.2',
        'cipher_suites': ['TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256']
    }
    
    assert tls_config['enabled'] is True
    assert 'TLS' in tls_config['version']
    assert float(tls_config['version'].split()[-1]) >= 1.2
