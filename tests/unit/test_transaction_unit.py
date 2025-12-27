import json
from unittest.mock import patch, MagicMock
from flask_jwt_extended import create_access_token


def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity="1")  # STRING!
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


@patch("routes.transaction.db.session")
@patch("routes.transaction.Transactions")
def test_create_transaction_success(mock_txn, mock_session, client, app):
    mock_txn.return_value.id = 1

    payload = {
        "total_price": 10000,
        "items": [
            {"vegetable_id": 1, "quantity": 2, "unit_price": 5000}
        ]
    }

    response = client.post(
        "/transaction/create",
        data=json.dumps(payload),
        headers=auth_headers(app)
    )

    assert response.status_code == 201
    assert "transaction_id" in response.json


@patch("routes.transaction.db.session")
@patch("routes.transaction.Transactions")
def test_update_transaction_success(mock_txn, mock_session, client, app):
    with app.app_context():
        mock_txn.query.get_or_404.return_value = MagicMock()

        response = client.post(
            "/transaction/update/1",
            data=json.dumps({"transaction_status": "paid"}),
            headers=auth_headers(app)
        )

    assert response.status_code == 200
    mock_session.commit.assert_called_once()


@patch("routes.transaction.DetailTransactions")
@patch("routes.transaction.Transactions")
def test_transaction_history(mock_txn, mock_detail, client, app):
    with app.app_context():
        fake_txn = MagicMock()
        fake_txn.id = 1
        fake_txn.code = "TRX1"
        fake_txn.total_price = 10000
        fake_txn.payment_method = "transfer"
        fake_txn.transaction_status = "paid"
        fake_txn.notes = None
        fake_txn.created_at = None

        mock_txn.query.filter_by.return_value.all.return_value = [fake_txn]
        mock_detail.query.filter_by.return_value.all.return_value = []

        response = client.get(
            "/transaction/history",
            headers=auth_headers(app)
        )

    assert response.status_code == 200
    assert isinstance(response.json, list)


@patch("routes.transaction.db.session")
@patch("routes.transaction.Transactions")
def test_delete_transaction_success(mock_txn, mock_session, client, app):
    with app.app_context():
        mock_txn.query.get_or_404.return_value = MagicMock()

        response = client.delete(
            "/transaction/delete/1",
            headers=auth_headers(app)
        )

    assert response.status_code == 200
    mock_session.delete.assert_called_once()
    mock_session.commit.assert_called_once()
