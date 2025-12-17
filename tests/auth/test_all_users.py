from unittest.mock import patch
from flask_jwt_extended import create_access_token
from tests.auth.mocks import MockUser

def test_all_users_admin(client, app):
    admin = MockUser(role="admin", sub_role="admin")
    users = [MockUser(id=1), MockUser(id=2)]

    with app.app_context():
        token = create_access_token(identity=str(admin.id))

    with patch("routes.auth.Users") as MockUsers:
        MockUsers.query.get.return_value = admin
        MockUsers.query.all.return_value = users

        response = client.get(
            "/auth/all",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert len(response.json) == 2
