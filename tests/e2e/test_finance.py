"""
End-to-end tests for Finance routes.
Tests: Summary, History with filters
"""
import pytest
from tests.conftest import get_auth_headers
from models.vegetables import Vegetables
from models.transactions import Transactions
from models.detail_transaction import DetailTransactions
from extensions import db


@pytest.fixture
def sample_transactions_for_finance(app, init_database):
    """Create multiple transactions for finance testing"""
    with app.app_context():
        from models.users import Users
        
        # Create vegetable
        veg = Vegetables(
            name="Finance Veg",
            price=10000.00,
            stock=100,
            category="daun",
            status="available",
            created_by=1
        )
        db.session.add(veg)
        db.session.commit()
        
        user = Users.query.filter_by(email="warga@test.com").first()
        
        # Transaction 1: Completed
        txn1 = Transactions(
            code="TRX001",
            user_id=user.id,
            total_price=50000.00,
            payment_method="transfer",
            transaction_status="completed"
        )
        db.session.add(txn1)
        
        # Transaction 2: Pending
        txn2 = Transactions(
            code="TRX002",
            user_id=user.id,
            total_price=30000.00,
            payment_method="cash",
            transaction_status="pending"
        )
        db.session.add(txn2)
        
        # Transaction 3: Cancelled
        txn3 = Transactions(
            code="TRX003",
            user_id=user.id,
            total_price=20000.00,
            payment_method="transfer",
            transaction_status="cancelled"
        )
        db.session.add(txn3)
        
        # Transaction 4: Completed
        txn4 = Transactions(
            code="TRX004",
            user_id=user.id,
            total_price=40000.00,
            payment_method="cash",
            transaction_status="completed"
        )
        db.session.add(txn4)
        
        db.session.commit()
        
        return [txn1.id, txn2.id, txn3.id, txn4.id]


class TestFinanceSummary:
    """Test cases for finance summary"""
    
    def test_summary_success(self, client, admin_token, sample_transactions_for_finance):
        """Test getting finance summary"""
        response = client.get(
            '/finance/summary',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Check all expected fields
        assert "total_income" in data
        assert "total_pending" in data
        assert "total_cancelled" in data
        assert "total_transactions" in data
        assert "completed_count" in data
        assert "pending_count" in data
        assert "cancelled_count" in data
    
    def test_summary_correct_calculations(self, client, admin_token, sample_transactions_for_finance):
        """Test that summary calculations are correct"""
        response = client.get(
            '/finance/summary',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify calculations based on sample data
        # Completed: 50000 + 40000 = 90000
        assert float(data["total_income"]) == 90000.00
        # Pending: 30000
        assert float(data["total_pending"]) == 30000.00
        # Cancelled: 20000
        assert float(data["total_cancelled"]) == 20000.00
        # Counts
        assert data["total_transactions"] == 4
        assert data["completed_count"] == 2
        assert data["pending_count"] == 1
        assert data["cancelled_count"] == 1
    
    def test_summary_empty_transactions(self, client, admin_token, init_database):
        """Test summary with no transactions"""
        response = client.get(
            '/finance/summary',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert float(data["total_income"]) == 0
        assert data["total_transactions"] == 0
    
    def test_summary_without_auth(self, client, init_database):
        """Test summary without authentication"""
        response = client.get('/finance/summary')
        assert response.status_code == 401


class TestFinanceHistory:
    """Test cases for finance history"""
    
    def test_history_all(self, client, admin_token, sample_transactions_for_finance):
        """Test getting all transaction history"""
        response = client.get(
            '/finance/history',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 4
    
    def test_history_filter_by_status_completed(self, client, admin_token, sample_transactions_for_finance):
        """Test filtering by completed status"""
        response = client.get(
            '/finance/history?status=completed',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        for txn in data:
            assert txn["transaction_status"] == "completed"
    
    def test_history_filter_by_status_pending(self, client, admin_token, sample_transactions_for_finance):
        """Test filtering by pending status"""
        response = client.get(
            '/finance/history?status=pending',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["transaction_status"] == "pending"
    
    def test_history_filter_by_status_cancelled(self, client, admin_token, sample_transactions_for_finance):
        """Test filtering by cancelled status"""
        response = client.get(
            '/finance/history?status=cancelled',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["transaction_status"] == "cancelled"
    
    def test_history_includes_all_fields(self, client, admin_token, sample_transactions_for_finance):
        """Test that history includes all expected fields"""
        response = client.get(
            '/finance/history',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        if len(data) > 0:
            txn = data[0]
            assert "id" in txn
            assert "code" in txn
            assert "user_id" in txn
            assert "total_price" in txn
            assert "payment_method" in txn
            assert "transaction_status" in txn
            assert "created_at" in txn
    
    def test_history_sorted_by_date(self, client, admin_token, sample_transactions_for_finance):
        """Test that history is sorted by created_at descending"""
        response = client.get(
            '/finance/history',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Should be sorted by date descending
        if len(data) > 1:
            dates = [txn["created_at"] for txn in data if txn["created_at"]]
            assert dates == sorted(dates, reverse=True)
    
    def test_history_without_auth(self, client, init_database):
        """Test history without authentication"""
        response = client.get('/finance/history')
        assert response.status_code == 401


class TestFinanceE2EFlow:
    """End-to-end finance flow tests"""
    
    def test_finance_after_transactions(self, client, warga_token, admin_token, init_database, app):
        """Test finance summary updates after transactions"""
        with app.app_context():
            # Create vegetable
            veg = Vegetables(
                name="E2E Finance Veg",
                price=10000.00,
                stock=100,
                category="daun",
                status="available",
                created_by=1
            )
            db.session.add(veg)
            db.session.commit()
            veg_id = veg.id
        
        # 1. Check initial summary (should be empty)
        summary1 = client.get(
            '/finance/summary',
            headers=get_auth_headers(admin_token)
        )
        assert summary1.status_code == 200
        initial_count = summary1.get_json()["total_transactions"]
        
        # 2. Create a transaction
        create_resp = client.post(
            '/transaction/create',
            headers=get_auth_headers(warga_token),
            json={
                "total_price": 25000,
                "payment_method": "transfer",
                "items": [{"vegetable_id": veg_id, "quantity": 1, "unit_price": 25000}]
            }
        )
        assert create_resp.status_code == 201
        txn_id = create_resp.get_json()["transaction_id"]
        
        # 3. Check summary - should have 1 more pending
        summary2 = client.get(
            '/finance/summary',
            headers=get_auth_headers(admin_token)
        )
        assert summary2.get_json()["total_transactions"] == initial_count + 1
        assert summary2.get_json()["pending_count"] >= 1
        
        # 4. Complete the transaction
        update_resp = client.post(
            f'/transaction/update/{txn_id}',
            headers=get_auth_headers(admin_token),
            json={"transaction_status": "completed"}
        )
        assert update_resp.status_code == 200
        
        # 5. Check summary - income should increase
        summary3 = client.get(
            '/finance/summary',
            headers=get_auth_headers(admin_token)
        )
        assert summary3.get_json()["completed_count"] >= 1
        assert float(summary3.get_json()["total_income"]) >= 25000
        
        # 6. Check finance history
        history = client.get(
            '/finance/history?status=completed',
            headers=get_auth_headers(admin_token)
        )
        assert history.status_code == 200
        assert len(history.get_json()) >= 1
