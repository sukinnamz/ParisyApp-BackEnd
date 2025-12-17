from unittest.mock import patch
from werkzeug.security import generate_password_hash
from tests.auth.mocks import MockUser

def test_login_success(client):
    user = MockUser()
    user.password = generate_password_hash("123")

    with patch("routes.auth.Users") as MockUsers:
        MockUsers.query.filter_by.return_value.first.return_value = user

        response = client.post("/auth/login", json={
            "email": "test@mail.com",
            "password": "123"
        })

        assert response.status_code == 200
        assert "token" in response.json
        assert response.json["user"]["email"] == "test@mail.com"


def test_login_failed(client):
    with patch("routes.auth.Users") as MockUsers:
        MockUsers.query.filter_by.return_value.first.return_value = None

        response = client.post("/auth/login", json={
            "email": "wrong@mail.com",
            "password": "wrong"
        })

        assert response.status_code == 401
