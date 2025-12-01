from extensions import db

class DetailTransactions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.id"))
    vegetable_id = db.Column(db.Integer, db.ForeignKey("vegetables.id"))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Numeric(10, 2))
    subtotal = db.Column(db.Numeric(10, 2))