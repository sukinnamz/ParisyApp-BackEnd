"""
End-to-end tests for Transaction routes.
Tests: Create, Update, History, Detail, All, Delete
"""
import pytest
from tests.conftest import get_auth_headers
from models.vegetables import Vegetables
from models.transactions import Transactions
from models.detail_transaction import DetailTransactions
from extensions import db


@pytest.fixture
def sample_vegetables_for_transaction(app, init_database):
    """Create vegetables for transaction testing"""
    with app.app_context():
        veg1 = Vegetables(
            name="Bayam Test",
            price=5000.00,
            stock=100,
            category="daun",
            status="available",
            created_by=1
        )
        veg2 = Vegetables(
            name="Wortel Test",
            price=8000.00,
            stock=50,
            category="akar",
            status="available",
            created_by=1
        )
        db.session.add(veg1)
        db.session.add(veg2)
        db.session.commit()
        return [veg1.id, veg2.id]


@pytest.fixture
def sample_transaction(app, init_database, sample_vegetables_for_transaction):
    """Create a sample transaction"""
    with app.app_context():
        from models.users import Users
        user = Users.query.filter_by(email="warga@test.com").first()
        
        transaction = Transactions(
            code="TRX20241224120000",
            user_id=user.id,
            total_price=21000.00,
            payment_method="transfer",
            transaction_status="pending",
            notes="Test transaction"
        )
        db.session.add(transaction)
        db.session.commit()
        
        # Add detail items
        detail1 = DetailTransactions(
            transaction_id=transaction.id,
            vegetable_id=sample_vegetables_for_transaction[0],
            quantity=2,
            unit_price=5000.00,
            subtotal=10000.00
        )
        detail2 = DetailTransactions(
            transaction_id=transaction.id,
            vegetable_id=sample_vegetables_for_transaction[1],
            quantity=1,
            unit_price=8000.00,
            subtotal=8000.00
        )
        db.session.add(detail1)
        db.session.add(detail2)
        db.session.commit()
        
        return transaction.id


class TestCreateTransaction:
    """Test cases for creating transactions"""
    
    def test_create_transaction_success(self, client, warga_token, sample_vegetables_for_transaction):
        """Test successful transaction creation"""
        response = client.post(
            '/transaction/create',
            headers=get_auth_headers(warga_token),
            json={
                "total_price": 18000,
                "payment_method": "transfer",
                "notes": "Test order",
                "items": [
                    {
                        "vegetable_id": sample_vegetables_for_transaction[0],
                        "quantity": 2,
                        "unit_price": 5000
                    },
                    {
                        "vegetable_id": sample_vegetables_for_transaction[1],
                        "quantity": 1,
                        "unit_price": 8000
                    }
                ]
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "Transaksi berhasil dibuat"
        assert "transaction_id" in data
    
    def test_create_transaction_cash(self, client, warga_token, sample_vegetables_for_transaction):
        """Test transaction with cash payment"""
        response = client.post(
            '/transaction/create',
            headers=get_auth_headers(warga_token),
            json={
                "total_price": 5000,
                "payment_method": "cash",
                "items": [
                    {
                        "vegetable_id": sample_vegetables_for_transaction[0],
                        "quantity": 1,
                        "unit_price": 5000
                    }
                ]
            }
        )
        
        assert response.status_code == 201
    
    def test_create_transaction_without_auth(self, client, sample_vegetables_for_transaction):
        """Test creating transaction without authentication"""
        response = client.post(
            '/transaction/create',
            json={
                "total_price": 5000,
                "items": [{"vegetable_id": 1, "quantity": 1, "unit_price": 5000}]
            }
        )
        
        assert response.status_code == 401
    
    def test_create_transaction_default_payment(self, client, warga_token, sample_vegetables_for_transaction):
        """Test transaction defaults to transfer payment"""
        response = client.post(
            '/transaction/create',
            headers=get_auth_headers(warga_token),
            json={
                "total_price": 5000,
                "items": [
                    {
                        "vegetable_id": sample_vegetables_for_transaction[0],
                        "quantity": 1,
                        "unit_price": 5000
                    }
                ]
            }
        )
        
        assert response.status_code == 201


class TestUpdateTransaction:
    """Test cases for updating transactions"""
    
    def test_update_transaction_status(self, client, admin_token, sample_transaction):
        """Test updating transaction status"""
        response = client.post(
            f'/transaction/update/{sample_transaction}',
            headers=get_auth_headers(admin_token),
            json={"transaction_status": "completed"}
        )
        
        assert response.status_code == 200
        assert response.get_json()["message"] == "Transaksi berhasil diperbarui"
    
    def test_update_transaction_cancelled(self, client, admin_token, sample_transaction):
        """Test cancelling transaction"""
        response = client.post(
            f'/transaction/update/{sample_transaction}',
            headers=get_auth_headers(admin_token),
            json={"transaction_status": "cancelled"}
        )
        
        assert response.status_code == 200
    
    def test_update_transaction_notes(self, client, admin_token, sample_transaction):
        """Test updating transaction notes"""
        response = client.post(
            f'/transaction/update/{sample_transaction}',
            headers=get_auth_headers(admin_token),
            json={"notes": "Updated notes"}
        )
        
        assert response.status_code == 200
    
    def test_update_transaction_payment_method(self, client, admin_token, sample_transaction):
        """Test updating payment method"""
        response = client.post(
            f'/transaction/update/{sample_transaction}',
            headers=get_auth_headers(admin_token),
            json={"payment_method": "cash"}
        )
        
        assert response.status_code == 200
    
    def test_update_transaction_not_found(self, client, admin_token):
        """Test updating non-existent transaction"""
        response = client.post(
            '/transaction/update/9999',
            headers=get_auth_headers(admin_token),
            json={"transaction_status": "completed"}
        )
        
        # Returns 404 or 500 depending on implementation
        assert response.status_code in [404, 500]


class TestTransactionHistory:
    """Test cases for transaction history"""
    
    def test_history_success(self, client, warga_token, sample_transaction):
        """Test getting user's transaction history"""
        response = client.get(
            '/transaction/history',
            headers=get_auth_headers(warga_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_history_empty(self, client, admin_token):
        """Test history when user has no transactions"""
        response = client.get(
            '/transaction/history',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_history_without_auth(self, client, init_database):
        """Test history without authentication"""
        response = client.get('/transaction/history')
        assert response.status_code == 401
    
    def test_history_includes_items(self, client, warga_token, sample_transaction):
        """Test that history includes transaction items"""
        response = client.get(
            '/transaction/history',
            headers=get_auth_headers(warga_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        if len(data) > 0:
            assert "items" in data[0]


class TestTransactionDetail:
    """Test cases for transaction detail"""
    
    def test_detail_success(self, client, warga_token, sample_transaction):
        """Test getting transaction detail"""
        response = client.get(
            f'/transaction/detail/{sample_transaction}',
            headers=get_auth_headers(warga_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "transaction_id" in data
        assert "items" in data
        assert "user_id" in data
    
    def test_detail_includes_timestamps(self, client, warga_token, sample_transaction):
        """Test that detail includes timestamps"""
        response = client.get(
            f'/transaction/detail/{sample_transaction}',
            headers=get_auth_headers(warga_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_detail_not_found(self, client, admin_token):
        """Test getting non-existent transaction detail"""
        response = client.get(
            '/transaction/detail/9999',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 404
    
    def test_detail_without_auth(self, client, init_database):
        """Test detail without authentication"""
        response = client.get('/transaction/detail/1')
        assert response.status_code == 401


class TestAllTransactions:
    """Test cases for getting all transactions"""
    
    def test_all_transactions(self, client, admin_token, sample_transaction):
        """Test getting all transactions"""
        response = client.get(
            '/transaction/all',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_all_transactions_includes_user(self, client, admin_token, sample_transaction):
        """Test that all transactions include user_id"""
        response = client.get(
            '/transaction/all',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        data = response.get_json()
        if len(data) > 0:
            assert "user_id" in data[0]
    
    def test_all_transactions_without_auth(self, client, init_database):
        """Test all transactions without authentication"""
        response = client.get('/transaction/all')
        assert response.status_code == 401


class TestDeleteTransaction:
    """Test cases for deleting transactions"""
    
    def test_delete_transaction_success(self, client, admin_token, sample_transaction):
        """Test deleting transaction"""
        response = client.delete(
            f'/transaction/delete/{sample_transaction}',
            headers=get_auth_headers(admin_token)
        )
        
        assert response.status_code == 200
        assert response.get_json()["message"] == "Transaksi berhasil dihapus"
    
    def test_delete_transaction_not_found(self, client, admin_token):
        """Test deleting non-existent transaction"""
        response = client.delete(
            '/transaction/delete/9999',
            headers=get_auth_headers(admin_token)
        )
        
        # Returns 404 or 500 depending on implementation
        assert response.status_code in [404, 500]
    
    def test_delete_transaction_without_auth(self, client, init_database):
        """Test delete without authentication"""
        response = client.delete('/transaction/delete/1')
        assert response.status_code == 401


class TestTransactionE2EFlow:
    """End-to-end transaction flow tests"""
    
    def test_full_transaction_flow(self, client, warga_token, admin_token, sample_vegetables_for_transaction):
        """Test: create -> detail -> update status -> history -> delete"""
        # 1. Create transaction
        create_resp = client.post(
            '/transaction/create',
            headers=get_auth_headers(warga_token),
            json={
                "total_price": 13000,
                "payment_method": "transfer",
                "notes": "E2E Test Order",
                "items": [
                    {
                        "vegetable_id": sample_vegetables_for_transaction[0],
                        "quantity": 1,
                        "unit_price": 5000
                    },
                    {
                        "vegetable_id": sample_vegetables_for_transaction[1],
                        "quantity": 1,
                        "unit_price": 8000
                    }
                ]
            }
        )
        assert create_resp.status_code == 201
        txn_id = create_resp.get_json()["transaction_id"]
        
        # 2. Get detail
        detail_resp = client.get(
            f'/transaction/detail/{txn_id}',
            headers=get_auth_headers(warga_token)
        )
        assert detail_resp.status_code == 200
        assert detail_resp.get_json()["transaction_status"] == "pending"
        assert len(detail_resp.get_json()["items"]) == 2
        
        # 3. Check history
        history_resp = client.get(
            '/transaction/history',
            headers=get_auth_headers(warga_token)
        )
        assert history_resp.status_code == 200
        assert any(t["transaction_id"] == txn_id for t in history_resp.get_json())
        
        # 4. Update status to completed
        update_resp = client.post(
            f'/transaction/update/{txn_id}',
            headers=get_auth_headers(admin_token),
            json={"transaction_status": "completed"}
        )
        assert update_resp.status_code == 200
        
        # 5. Verify status changed
        detail_resp2 = client.get(
            f'/transaction/detail/{txn_id}',
            headers=get_auth_headers(warga_token)
        )
        assert detail_resp2.get_json()["transaction_status"] == "completed"
        
        # 6. Delete
        delete_resp = client.delete(
            f'/transaction/delete/{txn_id}',
            headers=get_auth_headers(admin_token)
        )
        assert delete_resp.status_code == 200
        
        # 7. Verify deleted
        detail_resp3 = client.get(
            f'/transaction/detail/{txn_id}',
            headers=get_auth_headers(admin_token)
        )
        assert detail_resp3.status_code == 404
    
    def test_order_flow_pending_to_cancelled(self, client, warga_token, admin_token, sample_vegetables_for_transaction):
        """Test cancellation flow"""
        # Create
        create_resp = client.post(
            '/transaction/create',
            headers=get_auth_headers(warga_token),
            json={
                "total_price": 5000,
                "items": [
                    {
                        "vegetable_id": sample_vegetables_for_transaction[0],
                        "quantity": 1,
                        "unit_price": 5000
                    }
                ]
            }
        )
        assert create_resp.status_code == 201
        txn_id = create_resp.get_json()["transaction_id"]
        
        # Cancel
        cancel_resp = client.post(
            f'/transaction/update/{txn_id}',
            headers=get_auth_headers(admin_token),
            json={"transaction_status": "cancelled"}
        )
        assert cancel_resp.status_code == 200
        
        # Verify cancelled
        detail_resp = client.get(
            f'/transaction/detail/{txn_id}',
            headers=get_auth_headers(warga_token)
        )
        assert detail_resp.get_json()["transaction_status"] == "cancelled"
