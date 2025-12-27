from flask_jwt_extended import create_access_token
from unittest.mock import patch, MagicMock

# =========================
# LOGIN → LOGOUT FLOW
# =========================
def test_login_and_logout(client, init_database):
    # LOGIN REAL (pakai user dari conftest)
    login = client.post("/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })

    assert login.status_code == 200
    token = login.json["token"]

    # LOGOUT
    logout = client.get(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert logout.status_code == 200
    assert logout.json["message"] == "Logout berhasil"


# =========================
# ADMIN DELETE USER
# =========================
def test_admin_delete_user(client):
    token = create_access_token(identity="1")

    admin = MagicMock()
    admin.id = 1
    admin.sub_role = "admin"

    target_user = MagicMock()

    with patch("routes.auth.Users") as MockUser, \
         patch("routes.auth.db") as mock_db:

        MockUser.query.get_or_404.return_value = target_user
        MockUser.query.get.return_value = admin

        response = client.delete(
            "/auth/delete/2",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        mock_db.session.delete.assert_called()
        mock_db.session.commit.assert_called()
