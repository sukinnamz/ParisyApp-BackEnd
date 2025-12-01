from flask import Blueprint, request, jsonify
from extensions import db
from models.transactions import Transactions
from models.detail_transaction import DetailTransactions
from flask_jwt_extended import jwt_required, get_jwt_identity

transaction_bp = Blueprint("transaction", __name__)

@transaction_bp.post("/create")
@jwt_required()
def create():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        transaction = Transactions(
            user_id=user_id,
            total_amount=data["total_amount"],
            status="pending"
        )
        db.session.add(transaction)
        db.session.commit()

        for item in data["items"]:
            detail = DetailTransactions(
                transaction_id=transaction.id,
                vegetable_id=item["vegetable_id"],
                quantity=item["quantity"],
                price=item["price"]
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
        transaction.status = data.get("status", transaction.status)
        db.session.commit()
        return jsonify({"message": "Status transaksi berhasil diperbarui"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500


@transaction_bp.get("/history")
@jwt_required()
def history():
    user_id = get_jwt_identity()
    transactions = Transactions.query.filter_by(user_id=user_id).all()
    result = []
    for txn in transactions:
        details = DetailTransactions.query.filter_by(transaction_id=txn.id).all()
        items = []
        for detail in details:
            items.append({
                "vegetable_id": detail.vegetable_id,
                "quantity": detail.quantity,
                "price": str(detail.price)
            })
        result.append({
            "transaction_id": txn.id,
            "total_amount": str(txn.total_amount),
            "status": txn.status,
            "created_at": txn.created_at,
            "items": items
        })
    return jsonify(result)

@transaction_bp.get("/detail/<int:id>")
@jwt_required()
def detail(id):
    transaction = Transactions.query.get_or_404(id)
    details = DetailTransactions.query.filter_by(transaction_id=transaction.id).all()
    items = []
    for detail in details:
        items.append({
            "vegetable_id": detail.vegetable_id,
            "quantity": detail.quantity,
            "price": str(detail.price)
        })
    result = {
        "transaction_id": transaction.id,
        "user_id": transaction.user_id,
        "total_amount": str(transaction.total_amount),
        "status": transaction.status,
        "created_at": transaction.created_at,
        "items": items
    }
    return jsonify(result)

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

