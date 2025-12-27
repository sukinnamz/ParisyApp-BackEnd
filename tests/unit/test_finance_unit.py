from unittest.mock import patch, MagicMock
from datetime import datetime

# ==========================
# UNIT TEST: /finance/summary
# ==========================

def test_finance_summary_success(client):
    with patch(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request",
        return_value=None
    ), patch(
        "routes.finance.db"
    ) as mock_db, patch(
        "routes.finance.Transactions"
    ) as MockTransactions:

        # Mock sum hasil query
        mock_db.session.query.return_value.filter.return_value.scalar.side_effect = [
            100000,   # completed
            20000,    # pending
            5000      # cancelled
        ]

        # Mock count
        MockTransactions.query.count.return_value = 10
        MockTransactions.query.filter_by.side_effect = [
            MagicMock(count=lambda: 5),
            MagicMock(count=lambda: 3),
            MagicMock(count=lambda: 2),
        ]

        response = client.get("/finance/summary")

        assert response.status_code == 200
        data = response.get_json()

        assert data["total_income"] == "100000"
        assert data["total_pending"] == "20000"
        assert data["total_cancelled"] == "5000"
        assert data["total_transactions"] == 10
        assert data["completed_count"] == 5
        assert data["pending_count"] == 3
        assert data["cancelled_count"] == 2


# ==========================
# UNIT TEST: /finance/history
# ==========================

def test_finance_history_success(client):
    mock_txn = MagicMock(
        id=1,
        code="TRX001",
        user_id=2,
        total_price=50000,
        payment_method="transfer",
        transaction_status="completed",
        notes="test",
        created_at=datetime(2025, 1, 1),
        updated_at=datetime(2025, 1, 2)
    )

    with patch(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request",
        return_value=None
    ), patch(
        "routes.finance.Transactions"
    ) as MockTransactions:

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value.all.return_value = [mock_txn]

        MockTransactions.query = mock_query

        response = client.get("/finance/history?status=completed")

        assert response.status_code == 200
        data = response.get_json()

        assert len(data) == 1
        assert data[0]["code"] == "TRX001"
        assert data[0]["transaction_status"] == "completed"
        assert data[0]["total_price"] == "50000"
