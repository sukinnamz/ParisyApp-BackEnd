from unittest.mock import patch
from flask_jwt_extended import create_access_token
from tests.auth.mocks import MockUser

def test_delete_admin(client, app):
    admin = MockUser(id=1, role="admin")
    target = MockUser(id=2)

    with app.app_context():
        token = create_access_token(identity=str(admin.id))

    with patch("routes.auth.Users") as MockUsers, \
         patch("routes.auth.db.session") as mock_session:

        MockUsers.query.get_or_404.return_value = target
        MockUsers.query.get.return_value = admin

        response = client.delete(
            "/auth/delete/2",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        mock_session.delete.assert_called_once()
        mock_session.commit.assert_called_once()
