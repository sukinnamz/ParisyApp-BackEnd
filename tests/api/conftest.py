"""
Pytest configuration for API testing with authentication.
"""
import pytest
import requests
import random
import string

BASE_URL = "https://nitroir.pythonanywhere.com"
TIMEOUT = 30

# Store registered user data
_test_user = None
_test_token = None


def generate_random_string(length=8):
    """Generate random string"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def get_auth_headers(token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"} if token else {}


@pytest.fixture(scope="session")
def test_user():
    """Register a test user and return user data"""
    global _test_user, _test_token
    
    if _test_user and _test_token:
        return {"user": _test_user, "token": _test_token}
    
    email = f"test_{generate_random_string()}@test.com"
    password = "testpassword123"
    
    # Register user
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "name": "Test User",
        "email": email,
        "password": password,
        "role": "user",
        "sub_role": "warga"
    }, timeout=TIMEOUT)
    
    if response.status_code != 201:
        pytest.skip(f"Failed to register user: {response.text}")
    
    # Login to get token
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    }, timeout=TIMEOUT)
    
    if response.status_code != 200:
        pytest.skip(f"Failed to login: {response.text}")
    
    data = response.json()
    _test_user = data["user"]
    _test_user["password"] = password
    _test_token = data["token"]
    
    return {"user": _test_user, "token": _test_token}


@pytest.fixture(scope="session")
def auth_token(test_user):
    """Get authentication token"""
    return test_user["token"]


@pytest.fixture(scope="session")
def user_id(test_user):
    """Get user ID"""
    return test_user["user"]["id"]
