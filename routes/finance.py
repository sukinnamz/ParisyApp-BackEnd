from flask import Blueprint, request, jsonify
from extensions import db
from models.transactions import Transactions
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import func

finance_bp = Blueprint("finance", __name__)


@finance_bp.get("/summary")
@jwt_required()
def summary():
    try:
        # Total pendapatan (transaksi completed)
        total_income = db.session.query(func.sum(Transactions.total_price)).filter(
            Transactions.transaction_status == 'completed'
        ).scalar() or 0

        # Total transaksi pending
        total_pending = db.session.query(func.sum(Transactions.total_price)).filter(
            Transactions.transaction_status == 'pending'
        ).scalar() or 0

        # Total transaksi cancelled
        total_cancelled = db.session.query(func.sum(Transactions.total_price)).filter(
            Transactions.transaction_status == 'cancelled'
        ).scalar() or 0

        # Jumlah transaksi
        total_transactions = Transactions.query.count()
        completed_count = Transactions.query.filter_by(transaction_status='completed').count()
        pending_count = Transactions.query.filter_by(transaction_status='pending').count()
        cancelled_count = Transactions.query.filter_by(transaction_status='cancelled').count()

        result = {
            "total_income": str(total_income),
            "total_pending": str(total_pending),
            "total_cancelled": str(total_cancelled),
            "total_transactions": total_transactions,
            "completed_count": completed_count,
            "pending_count": pending_count,
            "cancelled_count": cancelled_count
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@finance_bp.get("/history")
@jwt_required()
def history():
    try:
        # Query parameters untuk filter
        status_filter = request.args.get('status')  # pending, completed, cancelled
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Transactions.query

        if status_filter:
            query = query.filter(Transactions.transaction_status == status_filter)
        if start_date:
            query = query.filter(Transactions.created_at >= start_date)
        if end_date:
            query = query.filter(Transactions.created_at <= end_date)

        transactions = query.order_by(Transactions.created_at.desc()).all()

        result = []
        for txn in transactions:
            result.append({
                "id": txn.id,
                "code": txn.code,
                "user_id": txn.user_id,
                "total_price": str(txn.total_price),
                "payment_method": txn.payment_method,
                "transaction_status": txn.transaction_status,
                "notes": txn.notes,
                "created_at": txn.created_at.isoformat() if txn.created_at else None,
                "updated_at": txn.updated_at.isoformat() if txn.updated_at else None
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
