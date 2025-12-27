"""
End-to-end tests for Authentication routes.
Tests: Register, Login, Logout, Profile, Edit, Delete, All Users
"""
import pytest
from tests.conftest import get_auth_headers


class TestRegister:
    """Test cases for user registration"""
    
    def test_register_success(self, client, init_database):
        """Test successful user registration"""
        response = client.post('/auth/register', json={
            "name": "New User",
            "email": "newuser@test.com",
            "password": "password123",
            "address": "New Address",
            "phone": "081234567899",
            "role": "user",
            "sub_role": "warga"
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "Registrasi berhasil"
    
    def test_register_duplicate_email(self, client, init_database):
        """Test registration with existing email"""
        response = client.post('/auth/register', json={
            "name": "Duplicate User",
            "email": "admin@test.com",
            "password": "password123",
            "role": "user",
            "sub_role": "warga"
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert data["message"] == "Email sudah terdaftar"
    
    def test_register_minimal_data(self, client, init_database):
        """Test registration with minimal required data"""
        response = client.post('/auth/register', json={
            "name": "Minimal User",
            "email": "minimal@test.com",
            "password": "password123"
        })
        
        assert response.status_code == 201


class TestLogin:
    """Test cases for user login"""
    
    def test_login_success(self, client, init_database):
        """Test successful login"""
        response = client.post('/auth/login', json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Login berhasil"
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == "admin@test.com"
    
    def test_login_wrong_password(self, client, init_database):
        """Test login with wrong password"""
        response = client.post('/auth/login', json={
            "email": "admin@test.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["message"] == "Email atau password salah"
    
    def test_login_nonexistent_user(self, client, init_database):
        """Test login with non-existent email"""
        response = client.post('/auth/login', json={
            "email": "nonexistent@test.com",
            "password": "password123"
        })
        
        assert response.status_code == 401


class TestLogout:
    """Test cases for user logout"""
    
    def test_logout_success(self, client, admin_token):
        """Test successful logout"""
        response = client.get(
            '/auth/logout',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Logout berhasil"
    
    def test_logout_without_token(self, client, init_database):
        """Test logout without authentication token"""
        response = client.get('/auth/logout')
        assert response.status_code == 401


class TestProfile:
    """Test cases for user profile"""
    
    def test_profile_own_data(self, client, admin_token, init_database, app):
        """Test getting own profile"""
        with app.app_context():
            from models.users import Users
            user = Users.query.filter_by(email="admin@test.com").first()
            user_id = user.id
        
        response = client.get(
            f'/auth/profile/{user_id}',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["email"] == "admin@test.com"
    
    def test_profile_without_token(self, client, init_database):
        """Test accessing profile without token"""
        response = client.get('/auth/profile/1')
        assert response.status_code == 401


class TestAllUsers:
    """Test cases for getting all users"""
    
    def test_all_users_admin(self, client, admin_token):
        """Test admin can see all users"""
        response = client.get(
            '/auth/all',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 5
    
    def test_all_users_warga_forbidden(self, client, warga_token):
        """Test warga cannot see all users"""
        response = client.get(
            '/auth/all',
            headers=get_auth_headers(warga_token)
        )
        
        assert response.status_code == 403


class TestEditUser:
    """Test cases for editing user profile"""
    
    def test_edit_own_profile(self, client, warga_token, init_database, app):
        """Test user can edit own profile"""
        with app.app_context():
            from models.users import Users
            warga = Users.query.filter_by(email="warga@test.com").first()
            warga_id = warga.id
        
        response = client.put(
            f'/auth/edit/{warga_id}',
            headers=get_auth_headers(warga_token),
            json={"name": "Updated Warga Name"}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Profil berhasil diperbarui"
        assert data["user"]["name"] == "Updated Warga Name"
    
    def test_edit_duplicate_email(self, client, admin_token, init_database, app):
        """Test editing with duplicate email fails"""
        with app.app_context():
            from models.users import Users
            warga = Users.query.filter_by(email="warga@test.com").first()
            warga_id = warga.id
        
        response = client.put(
            f'/auth/edit/{warga_id}',
            headers=get_auth_headers(admin_token),
            json={"email": "rw@test.com"}
        )
        
        assert response.status_code == 409


class TestAuthE2EFlow:
    """End-to-end authentication flow tests"""
    
    def test_full_auth_flow(self, client, init_database):
        """Test: register -> login -> profile -> edit -> logout"""
        # 1. Register
        register_resp = client.post('/auth/register', json={
            "name": "E2E User",
            "email": "e2e@test.com",
            "password": "e2epassword",
            "role": "user",
            "sub_role": "warga"
        })
        assert register_resp.status_code == 201
        
        # 2. Login
        login_resp = client.post('/auth/login', json={
            "email": "e2e@test.com",
            "password": "e2epassword"
        })
        assert login_resp.status_code == 200
        token = login_resp.get_json()["token"]
        user_id = login_resp.get_json()["user"]["id"]
        
        # 3. Get profile
        profile_resp = client.get(
            f'/auth/profile/{user_id}',
            headers=get_auth_headers(token)
        )
        assert profile_resp.status_code == 200
        assert profile_resp.get_json()["name"] == "E2E User"
        
        # 4. Edit profile
        edit_resp = client.put(
            f'/auth/edit/{user_id}',
            headers=get_auth_headers(token),
            json={"name": "Updated E2E User"}
        )
        assert edit_resp.status_code == 200
        
        # 5. Logout
        logout_resp = client.get(
            '/auth/logout',
            headers=get_auth_headers(token)
        )
        assert logout_resp.status_code == 200
