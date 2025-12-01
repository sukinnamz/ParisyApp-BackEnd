from extensions import db
from datetime import datetime

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.Enum('transfer', 'cash'))
    transaction_status = db.Column(db.Enum('pending', 'completed', 'cancelled'), default='pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
