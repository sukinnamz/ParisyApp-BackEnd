import json
from flask_jwt_extended import create_access_token
from models.transactions import Transactions
from extensions import db


def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity="1")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def test_create_transaction_integration(client, app):
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


def test_update_transaction_integration(client, app):
    with app.app_context():
        txn = Transactions(
            code="TRXINT",
            user_id=1,
            total_price=10000,
            payment_method="transfer",
            transaction_status="pending"
        )
        db.session.add(txn)
        db.session.commit()
        txn_id = txn.id

    response = client.post(
        f"/transaction/update/{txn_id}",
        data=json.dumps({"transaction_status": "paid"}),
        headers=auth_headers(app)
    )

    assert response.status_code == 200


def test_transaction_history_integration(client, app):
    response = client.get(
        "/transaction/history",
        headers=auth_headers(app)
    )

    assert response.status_code == 200


def test_delete_transaction_integration(client, app):
    with app.app_context():
        txn = Transactions(
            code="TRXDEL",
            user_id=1,
            total_price=5000,
            payment_method="cash",
            transaction_status="pending"
        )
        db.session.add(txn)
        db.session.commit()
        txn_id = txn.id

    response = client.delete(
        f"/transaction/delete/{txn_id}",
        headers=auth_headers(app)
    )

    assert response.status_code == 200
