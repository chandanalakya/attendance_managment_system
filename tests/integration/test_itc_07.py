"""ITC-07: Login + Session Timeout"""
import pytest
from unittest.mock import patch, Mock
import time

@patch('src.utils.session.st')
def test_itc_07_login_session_timeout(mock_st):
    """ITC-07: Login with session timeout validation"""
    from src.utils.session import check_session_timeout
    
    mock_st.session_state.authenticated = True
    mock_st.session_state.last_activity = time.time() - 1000
    
    with patch.object(mock_st, 'rerun'):
        check_session_timeout()
        assert mock_st.session_state.authenticated == False
