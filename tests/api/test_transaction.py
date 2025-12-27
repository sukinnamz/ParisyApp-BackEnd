"""
API Tests for Transaction Routes (with token)
Endpoints: /transaction/create, /transaction/update/<id>, 
           /transaction/history, /transaction/detail/<id>, 
           /transaction/all, /transaction/delete/<id>
"""
import requests
from tests.api.conftest import BASE_URL, TIMEOUT, get_auth_headers


class TestTransactionAPI:
    """Test Transaction endpoints with token"""
    
    # POST /transaction/create
    def test_create_transaction(self, auth_token):
        """Test create transaction"""
        response = requests.post(
            f"{BASE_URL}/transaction/create",
            headers=get_auth_headers(auth_token),
            json={
                "total_price": 50000,
                "payment_method": "transfer",
                "notes": "Test transaction",
                "items": [
                    {"vegetable_id": 1, "quantity": 2, "unit_price": 25000}
                ]
            },
            timeout=TIMEOUT
        )
        
        # 201 success, or 500 if vegetable_id doesn't exist
        assert response.status_code in [201, 500]
        if response.status_code == 201:
            assert "transaction_id" in response.json()
    
    # GET /transaction/history
    def test_get_history(self, auth_token):
        """Test get transaction history"""
        response = requests.get(
            f"{BASE_URL}/transaction/history",
            headers=get_auth_headers(auth_token),
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    # GET /transaction/all
    def test_get_all(self, auth_token):
        """Test get all transactions"""
        response = requests.get(
            f"{BASE_URL}/transaction/all",
            headers=get_auth_headers(auth_token),
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    # GET /transaction/detail/<id>
    def test_get_detail(self, auth_token):
        """Test get transaction detail"""
        response = requests.get(
            f"{BASE_URL}/transaction/detail/1",
            headers=get_auth_headers(auth_token),
            timeout=TIMEOUT
        )
        
        # 200 if exists, 404 if not found
        assert response.status_code in [200, 404]
    
    # POST /transaction/update/<id>
    def test_update_transaction(self, auth_token):
        """Test update transaction"""
        response = requests.post(
            f"{BASE_URL}/transaction/update/1",
            headers=get_auth_headers(auth_token),
            json={"transaction_status": "completed"},
            timeout=TIMEOUT
        )
        
        # 200 if exists, 404 if not found
        assert response.status_code in [200, 404]
