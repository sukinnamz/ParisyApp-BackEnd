from unittest.mock import patch
from flask_jwt_extended import create_access_token
from tests.auth.mocks import MockUser

def test_edit_self(client, app):
    user = MockUser(id=1)

    with app.app_context():
        token = create_access_token(identity=str(user.id))

    with patch("routes.auth.Users") as MockUsers, \
         patch("routes.auth.db.session") as mock_session:

        MockUsers.query.get_or_404.return_value = user
        MockUsers.query.get.return_value = user

        response = client.put(
            "/auth/edit/1",
            json={"name": "Updated"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json["user"]["name"] == "Updated"
        mock_session.commit.assert_called_once()
