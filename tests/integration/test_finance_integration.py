import pytest
from datetime import datetime

from extensions import db
from models.transactions import Transactions


# ======================================================
# FINANCE SUMMARY INTEGRATION TEST
# ======================================================

def test_finance_summary_integration(client, init_database, admin_token):
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }

    # Tambahkan data transaksi
    txn1 = Transactions(
        code="TXN001",
        user_id=1,
        total_price=10000,
        payment_method="cash",
        transaction_status="completed",
        notes="Test completed",
        created_at=datetime.utcnow()
    )

    txn2 = Transactions(
        code="TXN002",
        user_id=1,
        total_price=5000,
        payment_method="transfer",
        transaction_status="pending",
        notes="Test pending",
        created_at=datetime.utcnow()
    )

    db.session.add_all([txn1, txn2])
    db.session.commit()

    response = client.get("/finance/summary", headers=headers)

    assert response.status_code == 200

    data = response.get_json()
    assert data["total_income"] == "10000.00"
    assert data["total_pending"] == "5000.00"
    assert data["total_transactions"] == 2
    assert data["completed_count"] == 1
    assert data["pending_count"] == 1


# ======================================================
# FINANCE HISTORY - ALL DATA
# ======================================================

def test_finance_history_all_integration(client, init_database, admin_token):
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }

    txn = Transactions(
        code="TXN003",
        user_id=1,
        total_price=15000,
        payment_method="cash",
        transaction_status="completed",
        notes="History test",
        created_at=datetime.utcnow()
    )

    db.session.add(txn)
    db.session.commit()

    response = client.get("/finance/history", headers=headers)

    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["code"] == "TXN003"


# ======================================================
# FINANCE HISTORY - FILTER COMPLETED
# ======================================================

def test_finance_history_filter_completed(client, init_database, admin_token):
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }

    txn_completed = Transactions(
        code="TXN004",
        user_id=1,
        total_price=20000,
        payment_method="cash",
        transaction_status="completed",
        notes="Completed only",
        created_at=datetime.utcnow()
    )

    txn_pending = Transactions(
        code="TXN005",
        user_id=1,
        total_price=7000,
        payment_method="transfer",
        transaction_status="pending",
        notes="Should not appear",
        created_at=datetime.utcnow()
    )

    db.session.add_all([txn_completed, txn_pending])
    db.session.commit()

    response = client.get(
        "/finance/history?status=completed",
        headers=headers
    )

    assert response.status_code == 200

    data = response.get_json()
    assert len(data) == 1
    assert data[0]["transaction_status"] == "completed"
    assert data[0]["code"] == "TXN004"


# ======================================================
# FINANCE HISTORY - EMPTY RESULT
# ======================================================

def test_finance_history_empty(client, init_database, admin_token):
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }

    response = client.get(
        "/finance/history?status=cancelled",
        headers=headers
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data == []
