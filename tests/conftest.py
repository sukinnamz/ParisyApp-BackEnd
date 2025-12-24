"""
Pytest configuration and fixtures for end-to-end testing.
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models.users import Users
from models.vegetables import Vegetables
from models.transactions import Transactions
from models.detail_transaction import DetailTransactions
from werkzeug.security import generate_password_hash


class TestConfig:
    """Configuration for testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-secret-key"
    SECRET_KEY = "test-secret-key"
    SESSION_TYPE = "filesystem"


@pytest.fixture(scope="function")
def app():
    """Create application for testing"""
    application = create_app()
    application.config.from_object(TestConfig)
    
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope="function")
def init_database(app):
    """Initialize database with test data"""
    with app.app_context():
        # Create admin user
        admin_user = Users(
            name="Admin User",
            email="admin@test.com",
            password=generate_password_hash("admin123"),
            role="admin",
            sub_role="admin",
            address="Admin Address",
            phone="081234567890"
        )
        db.session.add(admin_user)
        
        # Create RW user
        rw_user = Users(
            name="RW User",
            email="rw@test.com",
            password=generate_password_hash("rw123"),
            role="user",
            sub_role="rw",
            address="RW Address",
            phone="081234567891"
        )
        db.session.add(rw_user)
        
        # Create RT user
        rt_user = Users(
            name="RT User",
            email="rt@test.com",
            password=generate_password_hash("rt123"),
            role="user",
            sub_role="rt",
            address="RT Address",
            phone="081234567892"
        )
        db.session.add(rt_user)
        
        # Create Warga user
        warga_user = Users(
            name="Warga User",
            email="warga@test.com",
            password=generate_password_hash("warga123"),
            role="user",
            sub_role="warga",
            address="Warga Address",
            phone="081234567893"
        )
        db.session.add(warga_user)
        
        # Create Sekretaris user
        sekretaris_user = Users(
            name="Sekretaris User",
            email="sekretaris@test.com",
            password=generate_password_hash("sekretaris123"),
            role="user",
            sub_role="sekretaris",
            address="Sekretaris Address",
            phone="081234567894"
        )
        db.session.add(sekretaris_user)
        
        db.session.commit()
        yield db
        db.session.remove()


@pytest.fixture
def admin_token(client, init_database):
    """Get JWT token for admin user"""
    response = client.post('/auth/login', json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    return response.get_json()["token"]


@pytest.fixture
def rw_token(client, init_database):
    """Get JWT token for RW user"""
    response = client.post('/auth/login', json={
        "email": "rw@test.com",
        "password": "rw123"
    })
    return response.get_json()["token"]


@pytest.fixture
def rt_token(client, init_database):
    """Get JWT token for RT user"""
    response = client.post('/auth/login', json={
        "email": "rt@test.com",
        "password": "rt123"
    })
    return response.get_json()["token"]


@pytest.fixture
def warga_token(client, init_database):
    """Get JWT token for Warga user"""
    response = client.post('/auth/login', json={
        "email": "warga@test.com",
        "password": "warga123"
    })
    return response.get_json()["token"]


@pytest.fixture
def sekretaris_token(client, init_database):
    """Get JWT token for Sekretaris user"""
    response = client.post('/auth/login', json={
        "email": "sekretaris@test.com",
        "password": "sekretaris123"
    })
    return response.get_json()["token"]


def get_auth_headers(token):
    """Helper function to get authorization headers"""
    return {"Authorization": f"Bearer {token}"}
