from unittest.mock import patch

def test_register_success(client):
    payload = {
        "name": "Innama",
        "email": "innama@mail.com",
        "password": "123456"
    }

    with patch("routes.auth.Users") as MockUsers, \
         patch("routes.auth.db.session") as mock_session:

        MockUsers.query.filter_by.return_value.first.return_value = None

        response = client.post("/auth/register", json=payload)

        assert response.status_code == 201
        assert response.json["message"] == "Registrasi berhasil"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


def test_register_email_exists(client):
    with patch("routes.auth.Users") as MockUsers:
        MockUsers.query.filter_by.return_value.first.return_value = True

        response = client.post("/auth/register", json={
            "email": "exist@mail.com",
            "password": "123"
        })

        assert response.status_code == 409
