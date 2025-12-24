"""
End-to-end tests for Vegetable routes.
Tests: List, Get, Add, Update, Delete, Search, Admin List
"""
import pytest
from tests.conftest import get_auth_headers
from models.vegetables import Vegetables
from extensions import db


@pytest.fixture
def sample_vegetable(app, init_database):
    """Create a sample vegetable for testing"""
    with app.app_context():
        vegetable = Vegetables(
            name="Bayam Segar",
            description="Bayam organik segar",
            price=5000.00,
            stock=100,
            image="https://example.com/bayam.jpg",
            category="daun",
            status="available",
            created_by=1
        )
        db.session.add(vegetable)
        db.session.commit()
        return vegetable.id


@pytest.fixture
def sample_vegetables(app, init_database):
    """Create multiple sample vegetables"""
    with app.app_context():
        vegetables_data = [
            {"name": "Bayam Hijau", "price": 5000.00, "stock": 100, "category": "daun", "status": "available"},
            {"name": "Wortel", "price": 8000.00, "stock": 50, "category": "akar", "status": "available"},
            {"name": "Brokoli", "price": 15000.00, "stock": 30, "category": "bunga", "status": "available"},
            {"name": "Tomat", "price": 10000.00, "stock": 80, "category": "buah", "status": "available"},
            {"name": "Kangkung", "price": 4000.00, "stock": 0, "category": "daun", "status": "unavailable"},
        ]
        
        veg_ids = []
        for veg_data in vegetables_data:
            veg = Vegetables(created_by=1, **veg_data)
            db.session.add(veg)
            db.session.flush()
            veg_ids.append(veg.id)
        
        db.session.commit()
        return veg_ids


class TestListVegetables:
    """Test cases for listing vegetables"""
    
    def test_list_vegetables_empty(self, client, init_database):
        """Test list when no vegetables exist"""
        response = client.get('/vegetable/list')
        assert response.status_code == 200
        assert response.get_json() == []
    
    def test_list_vegetables_with_data(self, client, sample_vegetables):
        """Test list with vegetables"""
        response = client.get('/vegetable/list')
        assert response.status_code == 200
        data = response.get_json()
        # Should only return available vegetables
        assert len(data) == 4
        for veg in data:
            assert veg["status"] == "available"
    
    def test_list_no_auth_required(self, client, sample_vegetable):
        """Test that list doesn't require authentication"""
        response = client.get('/vegetable/list')
        assert response.status_code == 200


class TestGetVegetable:
    """Test cases for getting single vegetable"""
    
    def test_get_vegetable_success(self, client, sample_vegetable):
        """Test get single vegetable"""
        response = client.get(f'/vegetable/get/{sample_vegetable}')
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Bayam Segar"
        assert data["category"] == "daun"
    
    def test_get_vegetable_not_found(self, client, init_database):
        """Test get non-existent vegetable"""
        response = client.get('/vegetable/get/9999')
        assert response.status_code == 404


class TestGetByCategory:
    """Test cases for getting vegetables by category"""
    
    def test_get_by_category(self, client, sample_vegetables):
        """Test get vegetables by category"""
        response = client.get('/vegetable/by-category/daun')
        assert response.status_code == 200
        data = response.get_json()
        # Only available vegetables with category 'daun'
        assert len(data) == 1
        assert data[0]["name"] == "Bayam Hijau"
    
    def test_get_by_category_empty(self, client, init_database):
        """Test get by category with no results"""
        response = client.get('/vegetable/by-category/bunga')
        assert response.status_code == 200
        assert response.get_json() == []


class TestAddVegetable:
    """Test cases for adding vegetables"""
    
    def test_add_vegetable_as_admin(self, client, admin_token):
        """Test admin can add vegetable"""
        response = client.post(
            '/vegetable/add',
            headers=get_auth_headers(admin_token),
            json={
                "name": "Sawi Baru",
                "description": "Sawi hijau segar",
                "price": 6000,
                "stock": 50,
                "category": "daun",
                "status": "available"
            }
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "Sayuran berhasil ditambahkan"
        assert data["vegetable"]["name"] == "Sawi Baru"
    
    def test_add_vegetable_as_rt(self, client, rt_token):
        """Test RT can add vegetable"""
        response = client.post(
            '/vegetable/add',
            headers=get_auth_headers(rt_token),
            json={
                "name": "Selada RT",
                "price": 7000,
                "category": "daun"
            }
        )
        assert response.status_code == 201
    
    def test_add_vegetable_as_warga_forbidden(self, client, warga_token):
        """Test warga cannot add vegetable"""
        response = client.post(
            '/vegetable/add',
            headers=get_auth_headers(warga_token),
            json={
                "name": "Sawi Warga",
                "price": 6000,
                "category": "daun"
            }
        )
        assert response.status_code == 403
    
    def test_add_vegetable_duplicate_name(self, client, admin_token, sample_vegetable):
        """Test adding duplicate vegetable name"""
        response = client.post(
            '/vegetable/add',
            headers=get_auth_headers(admin_token),
            json={
                "name": "Bayam Segar",
                "price": 6000,
                "category": "daun"
            }
        )
        assert response.status_code == 409
    
    def test_add_vegetable_missing_required(self, client, admin_token):
        """Test adding vegetable without required fields"""
        response = client.post(
            '/vegetable/add',
            headers=get_auth_headers(admin_token),
            json={"description": "Only description"}
        )
        assert response.status_code == 400


class TestUpdateVegetable:
    """Test cases for updating vegetables"""
    
    def test_update_vegetable_success(self, client, admin_token, sample_vegetable):
        """Test update vegetable"""
        response = client.put(
            f'/vegetable/update/{sample_vegetable}',
            headers=get_auth_headers(admin_token),
            json={
                "name": "Bayam Updated",
                "price": 7000
            }
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["vegetable"]["name"] == "Bayam Updated"
        assert data["vegetable"]["price"] == "7000.00"
    
    def test_update_vegetable_not_found(self, client, admin_token):
        """Test update non-existent vegetable"""
        response = client.put(
            '/vegetable/update/9999',
            headers=get_auth_headers(admin_token),
            json={"name": "New Name"}
        )
        assert response.status_code == 404
    
    def test_update_vegetable_forbidden(self, client, warga_token, sample_vegetable):
        """Test warga cannot update vegetable"""
        response = client.put(
            f'/vegetable/update/{sample_vegetable}',
            headers=get_auth_headers(warga_token),
            json={"name": "Hacked Name"}
        )
        assert response.status_code == 403


class TestDeleteVegetable:
    """Test cases for deleting vegetables"""
    
    def test_delete_vegetable_success(self, client, admin_token, sample_vegetable):
        """Test delete vegetable"""
        response = client.delete(
            f'/vegetable/delete/{sample_vegetable}',
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 200
        assert response.get_json()["message"] == "Sayuran berhasil dihapus"
    
    def test_delete_vegetable_forbidden(self, client, warga_token, sample_vegetable):
        """Test warga cannot delete vegetable"""
        response = client.delete(
            f'/vegetable/delete/{sample_vegetable}',
            headers=get_auth_headers(warga_token)
        )
        assert response.status_code == 403


class TestUpdateStock:
    """Test cases for updating stock"""
    
    def test_update_stock_as_admin(self, client, admin_token, sample_vegetable):
        """Test admin can update stock"""
        response = client.put(
            f'/vegetable/update-stock/{sample_vegetable}',
            headers=get_auth_headers(admin_token),
            json={"stock": 200}
        )
        assert response.status_code == 200
        assert response.get_json()["vegetable"]["stock"] == 200
    
    def test_update_stock_as_sekretaris(self, client, sekretaris_token, sample_vegetable):
        """Test sekretaris can update stock"""
        response = client.put(
            f'/vegetable/update-stock/{sample_vegetable}',
            headers=get_auth_headers(sekretaris_token),
            json={"stock": 150}
        )
        assert response.status_code == 200
    
    def test_update_stock_as_warga_forbidden(self, client, warga_token, sample_vegetable):
        """Test warga cannot update stock"""
        response = client.put(
            f'/vegetable/update-stock/{sample_vegetable}',
            headers=get_auth_headers(warga_token),
            json={"stock": 999}
        )
        assert response.status_code == 403
    
    def test_update_stock_missing_field(self, client, admin_token, sample_vegetable):
        """Test update stock without stock field"""
        response = client.put(
            f'/vegetable/update-stock/{sample_vegetable}',
            headers=get_auth_headers(admin_token),
            json={}
        )
        assert response.status_code == 400


class TestUpdateStatus:
    """Test cases for updating status"""
    
    def test_update_status_success(self, client, admin_token, sample_vegetable):
        """Test update status"""
        response = client.put(
            f'/vegetable/update-status/{sample_vegetable}',
            headers=get_auth_headers(admin_token),
            json={"status": "unavailable"}
        )
        assert response.status_code == 200
        assert response.get_json()["vegetable"]["status"] == "unavailable"
    
    def test_update_status_invalid(self, client, admin_token, sample_vegetable):
        """Test update with invalid status"""
        response = client.put(
            f'/vegetable/update-status/{sample_vegetable}',
            headers=get_auth_headers(admin_token),
            json={"status": "invalid_status"}
        )
        assert response.status_code == 400


class TestSearchVegetables:
    """Test cases for searching vegetables"""
    
    def test_search_by_name(self, client, sample_vegetables):
        """Test search by name"""
        response = client.get('/vegetable/search?q=Bayam')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        assert all('Bayam' in veg['name'] for veg in data)
    
    def test_search_by_category(self, client, sample_vegetables):
        """Test search by category"""
        response = client.get('/vegetable/search?category=akar')
        assert response.status_code == 200
        data = response.get_json()
        assert all(veg['category'] == 'akar' for veg in data)
    
    def test_search_combined(self, client, sample_vegetables):
        """Test search with name and category"""
        response = client.get('/vegetable/search?q=Bayam&category=daun')
        assert response.status_code == 200
    
    def test_search_empty(self, client, sample_vegetables):
        """Test search with no results"""
        response = client.get('/vegetable/search?q=XYZ123NotExist')
        assert response.status_code == 200
        assert response.get_json() == []


class TestAdminList:
    """Test cases for admin list"""
    
    def test_admin_list_success(self, client, admin_token, sample_vegetables):
        """Test admin can see all vegetables including unavailable"""
        response = client.get(
            '/vegetable/admin/list',
            headers=get_auth_headers(admin_token)
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 5  # Including unavailable
    
    def test_admin_list_as_warga_forbidden(self, client, warga_token, sample_vegetables):
        """Test warga cannot access admin list"""
        response = client.get(
            '/vegetable/admin/list',
            headers=get_auth_headers(warga_token)
        )
        assert response.status_code == 403


class TestVegetableE2EFlow:
    """End-to-end vegetable management flow"""
    
    def test_full_vegetable_flow(self, client, admin_token):
        """Test: add -> get -> update -> update stock -> delete"""
        # 1. Add
        add_resp = client.post(
            '/vegetable/add',
            headers=get_auth_headers(admin_token),
            json={
                "name": "E2E Vegetable",
                "price": 5000,
                "stock": 100,
                "category": "daun"
            }
        )
        assert add_resp.status_code == 201
        veg_id = add_resp.get_json()["vegetable"]["id"]
        
        # 2. Get
        get_resp = client.get(f'/vegetable/get/{veg_id}')
        assert get_resp.status_code == 200
        assert get_resp.get_json()["name"] == "E2E Vegetable"
        
        # 3. Update
        update_resp = client.put(
            f'/vegetable/update/{veg_id}',
            headers=get_auth_headers(admin_token),
            json={"name": "Updated E2E", "price": 7000}
        )
        assert update_resp.status_code == 200
        
        # 4. Update stock
        stock_resp = client.put(
            f'/vegetable/update-stock/{veg_id}',
            headers=get_auth_headers(admin_token),
            json={"stock": 200}
        )
        assert stock_resp.status_code == 200
        
        # 5. Delete
        delete_resp = client.delete(
            f'/vegetable/delete/{veg_id}',
            headers=get_auth_headers(admin_token)
        )
        assert delete_resp.status_code == 200
        
        # 6. Verify deleted
        get_resp2 = client.get(f'/vegetable/get/{veg_id}')
        assert get_resp2.status_code == 404
