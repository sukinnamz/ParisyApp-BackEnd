from flask import Blueprint, request, jsonify
from extensions import db
from models.transactions import Transactions
from models.detail_transaction import DetailTransactions
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

transaction_bp = Blueprint("transaction", __name__)


def detail_item_data(detail):
    """Serialize detail transaction item"""
    return {
        "vegetable_id": detail.vegetable_id,
        "quantity": detail.quantity,
        "unit_price": str(detail.unit_price),
        "subtotal": str(detail.subtotal)
    }


def transaction_data(txn, include_user=False, include_timestamps=False):
    """Serialize transaction data"""
    data = {
        "transaction_id": txn.id,
        "code": txn.code,
        "total_price": str(txn.total_price),
        "payment_method": txn.payment_method,
        "transaction_status": txn.transaction_status,
        "notes": txn.notes,
        "created_at": txn.created_at.isoformat() if txn.created_at else None,
    }
    if include_user:
        data["user_id"] = txn.user_id
    if include_timestamps:
        data["updated_at"] = txn.updated_at.isoformat() if txn.updated_at else None
    return data


def transaction_with_items(txn, include_user=False, include_timestamps=False):
    """Serialize transaction with its detail items"""
    details = DetailTransactions.query.filter_by(transaction_id=txn.id).all()
    data = transaction_data(txn, include_user, include_timestamps)
    data["items"] = [detail_item_data(d) for d in details]
    return data


@transaction_bp.post("/create")
@jwt_required()
def create():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        code = f"TRX{datetime.now().strftime('%Y%m%d%H%M%S')}"

        transaction = Transactions(
            code=code,
            user_id=user_id,
            total_price=data["total_price"],
            payment_method=data.get("payment_method", "transfer"),
            transaction_status="pending",
            notes=data.get("notes")
        )
        db.session.add(transaction)
        db.session.commit()

        for item in data["items"]:
            detail = DetailTransactions(
                transaction_id=transaction.id,
                vegetable_id=item["vegetable_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                subtotal=item["quantity"] * item["unit_price"]
            )
            db.session.add(detail)

        db.session.commit()

        return jsonify({"message": "Transaksi berhasil dibuat", "transaction_id": transaction.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500
    
@transaction_bp.post("/update/<int:id>")
@jwt_required()
def update(id):
    try:
        data = request.get_json()
        transaction = Transactions.query.get_or_404(id)
        transaction.transaction_status = data.get("transaction_status", transaction.transaction_status)
        if "payment_method" in data:
            transaction.payment_method = data["payment_method"]
        if "notes" in data:
            transaction.notes = data["notes"]
        db.session.commit()
        return jsonify({"message": "Transaksi berhasil diperbarui"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500


@transaction_bp.get("/history")
@jwt_required()
def history():
    user_id = get_jwt_identity()
    transactions = Transactions.query.filter_by(user_id=user_id).all()
    return jsonify([transaction_with_items(txn) for txn in transactions])


@transaction_bp.get("/detail/<int:id>")
@jwt_required()
def detail(id):
    transaction = Transactions.query.get_or_404(id)
    return jsonify(transaction_with_items(transaction, include_user=True, include_timestamps=True))


@transaction_bp.get("/all")
@jwt_required()
def get_all():
    transactions = Transactions.query.all()
    return jsonify([transaction_with_items(txn, include_user=True, include_timestamps=True) for txn in transactions])


@transaction_bp.delete("/delete/<int:id>")
@jwt_required()
def delete(id):
    try:
        transaction = Transactions.query.get_or_404(id)
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({"message": "Transaksi berhasil dihapus"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

