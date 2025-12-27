"""
API Tests for Vegetable Routes (with token)
Endpoints: /vegetable/list, /vegetable/get/<id>, /vegetable/by-category/<category>,
           /vegetable/add, /vegetable/update/<id>, /vegetable/delete/<id>,
           /vegetable/admin/list, /vegetable/update-stock/<id>, /vegetable/search
"""
import requests
from tests.api.conftest import BASE_URL, TIMEOUT, get_auth_headers, generate_random_string


class TestVegetableAPI:
    """Test Vegetable endpoints with token"""
    
    # GET /vegetable/list (public)
    def test_get_list(self):
        """Test get vegetable list (public endpoint)"""
        response = requests.get(f"{BASE_URL}/vegetable/list", timeout=TIMEOUT)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    # GET /vegetable/get/<id>
    def test_get_by_id(self):
        """Test get vegetable by id"""
        response = requests.get(f"{BASE_URL}/vegetable/get/1", timeout=TIMEOUT)
        
        # 200 if exists, 404 if not found
        assert response.status_code in [200, 404]
    
    # GET /vegetable/by-category/<category>
    def test_get_by_category(self):
        """Test get vegetables by category"""
        response = requests.get(f"{BASE_URL}/vegetable/by-category/daun", timeout=TIMEOUT)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    # GET /vegetable/search
    def test_search(self):
        """Test search vegetables"""
        response = requests.get(f"{BASE_URL}/vegetable/search?q=bayam", timeout=TIMEOUT)
        
        assert response.status_code in [200, 404]
    
    # POST /vegetable/add (requires permission)
    def test_add_vegetable(self, auth_token):
        """Test add vegetable (may fail if not admin/rw/rt)"""
        response = requests.post(
            f"{BASE_URL}/vegetable/add",
            headers=get_auth_headers(auth_token),
            json={
                "name": f"Test Sayur {generate_random_string()}",
                "price": 15000,
                "category": "daun",
                "stock": 100,
                "description": "Sayuran test"
            },
            timeout=TIMEOUT
        )
        
        # 201 if has permission, 403 if not
        assert response.status_code in [201, 403]
    
    # GET /vegetable/admin/list (requires permission)
    def test_admin_list(self, auth_token):
        """Test admin list (may fail if not authorized)"""
        response = requests.get(
            f"{BASE_URL}/vegetable/admin/list",
            headers=get_auth_headers(auth_token),
            timeout=TIMEOUT
        )
        
        # 200 if has permission, 403 if not
        assert response.status_code in [200, 403]
    
    # PUT /vegetable/update/<id> (requires permission)
    def test_update_vegetable(self, auth_token):
        """Test update vegetable (may fail if not admin/rw/rt)"""
        response = requests.put(
            f"{BASE_URL}/vegetable/update/1",
            headers=get_auth_headers(auth_token),
            json={"description": "Updated description"},
            timeout=TIMEOUT
        )
        
        # 200 if has permission, 403 if not, 404 if not found
        assert response.status_code in [200, 403, 404]
    
    # PUT /vegetable/update-stock/<id> (requires admin/sekretaris)
    def test_update_stock(self, auth_token):
        """Test update stock (may fail if not admin/sekretaris)"""
        response = requests.put(
            f"{BASE_URL}/vegetable/update-stock/1",
            headers=get_auth_headers(auth_token),
            json={"stock": 50},
            timeout=TIMEOUT
        )
        
        # 200 if has permission, 403 if not, 404 if not found
        assert response.status_code in [200, 403, 404]
