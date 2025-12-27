"""
API Tests for Auth Routes (with token)
Endpoints: /auth/register, /auth/login, /auth/logout, 
           /auth/profile/<id>, /auth/all, /auth/edit/<id>
"""
import pytest
import requests
from tests.api.conftest import BASE_URL, TIMEOUT, get_auth_headers, generate_random_string


class TestAuthAPI:
    """Test Auth endpoints with token"""
    
    # POST /auth/register
    def test_register(self):
        """Test registration"""
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "name": "New User",
            "email": f"newuser_{generate_random_string()}@test.com",
            "password": "password123",
            "role": "user",
            "sub_role": "warga"
        }, timeout=TIMEOUT)
        
        assert response.status_code == 201
        assert response.json()["message"] == "Registrasi berhasil"
    
    # POST /auth/login
    def test_login(self, test_user):
        """Test login"""
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": test_user["user"]["email"],
            "password": test_user["user"]["password"]
        }, timeout=TIMEOUT)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login berhasil"
        assert "token" in data
        assert "user" in data
    
    # GET /auth/logout
    def test_logout(self, auth_token):
        """Test logout with token"""
        response = requests.get(
            f"{BASE_URL}/auth/logout",
            headers=get_auth_headers(auth_token),
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Logout berhasil"
    
    # GET /auth/profile/<id>
    def test_get_profile(self, auth_token, user_id):
        """Test get own profile"""
        response = requests.get(
            f"{BASE_URL}/auth/profile/{user_id}",
            headers=get_auth_headers(auth_token),
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
    
    # GET /auth/all
    def test_get_all_users(self, auth_token):
        """Test get all users (may fail if not admin/rw/rt)"""
        response = requests.get(
            f"{BASE_URL}/auth/all",
            headers=get_auth_headers(auth_token),
            timeout=TIMEOUT
        )
        
        # 200 if authorized, 403 if not admin/rw/rt
        assert response.status_code in [200, 403]
    
    # PUT /auth/edit/<id>
    def test_edit_profile(self, auth_token, user_id):
        """Test edit own profile"""
        response = requests.put(
            f"{BASE_URL}/auth/edit/{user_id}",
            headers=get_auth_headers(auth_token),
            json={"name": "Updated Name"},
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Profil berhasil diperbarui"
