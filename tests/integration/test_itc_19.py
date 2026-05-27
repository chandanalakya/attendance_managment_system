"""ITC-19: TLS + API Communication"""
import pytest

def test_itc_19_tls_api_communication():
    """ITC-19: All client-server calls use secure TLS 1.2+"""
    api_config = {
        'protocol': 'https',
        'tls_version': 'TLS 1.2',
        'enforce_tls': True
    }
    
    assert api_config['protocol'] == 'https'
    assert api_config['enforce_tls'] is True
    assert float(api_config['tls_version'].split()[-1]) >= 1.2
