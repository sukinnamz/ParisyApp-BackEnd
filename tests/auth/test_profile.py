from unittest.mock import patch
from flask_jwt_extended import create_access_token
from tests.auth.mocks import MockUser

def test_profile_self_access(client, app):
    user = MockUser(id=1)

    with app.app_context():
        token = create_access_token(identity=str(user.id))

    with patch("routes.auth.Users") as MockUsers:
        MockUsers.query.get_or_404.return_value = user
        MockUsers.query.get.return_value = user

        response = client.get(
            "/auth/profile/1",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["email"] == "test@mail.com"


def test_profile_unauthorized(client, app):
    target_user = MockUser(id=2)
    current_user = MockUser(id=1, role="user", sub_role="warga")

    with app.app_context():
        token = create_access_token(identity=str(current_user.id))

    with patch("routes.auth.Users") as MockUsers:
        MockUsers.query.get_or_404.return_value = target_user
        MockUsers.query.get.return_value = current_user

        response = client.get(
            "/auth/profile/2",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
