"""
API Tests for Finance Routes (with token)
Endpoints: /finance/summary, /finance/history
"""
import requests
from tests.api.conftest import BASE_URL, TIMEOUT, get_auth_headers


class TestFinanceAPI:
    """Test Finance endpoints with token"""
    
    # GET /finance/summary
    def test_get_summary(self, auth_token):
        """Test get finance summary"""
        response = requests.get(
            f"{BASE_URL}/finance/summary",
            headers=get_auth_headers(auth_token),
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data
        assert "total_transactions" in data
    
    # GET /finance/history
    def test_get_history(self, auth_token):
        """Test get finance history"""
        response = requests.get(
            f"{BASE_URL}/finance/history",
            headers=get_auth_headers(auth_token),
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    # GET /finance/history with filter
    def test_get_history_with_filter(self, auth_token):
        """Test get finance history with status filter"""
        response = requests.get(
            f"{BASE_URL}/finance/history?status=completed",
            headers=get_auth_headers(auth_token),
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
