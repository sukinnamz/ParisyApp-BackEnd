from unittest.mock import patch, MagicMock
from flask_jwt_extended import create_access_token

# =========================
# UNIT TEST REGISTER
# =========================
def test_register_success(client):
    with patch("routes.auth.Users") as MockUser, \
         patch("routes.auth.db") as mock_db:

        MockUser.query.filter_by.return_value.first.return_value = None

        response = client.post("/auth/register", json={
            "name": "Test",
            "email": "test@mail.com",
            "password": "123"
        })

        assert response.status_code == 201
        assert response.json["message"] == "Registrasi berhasil"
        mock_db.session.add.assert_called()
        mock_db.session.commit.assert_called()


def test_register_email_exists(client):
    with patch("routes.auth.Users") as MockUser:
        MockUser.query.filter_by.return_value.first.return_value = MagicMock()

        response = client.post("/auth/register", json={
            "name": "Test",
            "email": "test@mail.com",
            "password": "123"
        })

        assert response.status_code == 409


# =========================
# UNIT TEST LOGIN
# =========================
def test_login_success(client):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.password = "hashed"
    mock_user.name = "Test"
    mock_user.email = "test@mail.com"
    mock_user.role = "user"
    mock_user.sub_role = "warga"

    with patch("routes.auth.Users") as MockUser, \
         patch("routes.auth.check_password_hash", return_value=True):

        MockUser.query.filter_by.return_value.first.return_value = mock_user

        response = client.post("/auth/login", json={
            "email": "test@mail.com",
            "password": "123"
        })

        assert response.status_code == 200
        assert "token" in response.json


def test_login_failed(client):
    with patch("routes.auth.Users") as MockUser:
        MockUser.query.filter_by.return_value.first.return_value = None

        response = client.post("/auth/login", json={
            "email": "x@mail.com",
            "password": "wrong"
        })

        assert response.status_code == 401


# =========================
# UNIT TEST PROFILE (UNAUTHORIZED)
# =========================
def test_profile_unauthorized(client):
    mock_target_user = MagicMock(id=1)

    mock_current_user = MagicMock(
        id=2,
        role="user",
        sub_role="warga"
    )

    with patch(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request",
        return_value=None
    ), patch(
        "routes.auth.get_jwt_identity",
        return_value=2
    ), patch(
        "routes.auth.Users"
    ) as MockUser:

        MockUser.query.get_or_404.return_value = mock_target_user
        MockUser.query.get.return_value = mock_current_user

        response = client.get("/auth/profile/1")

        assert response.status_code == 403