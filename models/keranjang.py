from extensions import db
from datetime import datetime

class Keranjang(db.Model):
    id_cart = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer, db.ForeignKey("user.id_user"))
    id_sayur = db.Column(db.Integer, db.ForeignKey("sayur.id_sayur"))
    jumlah = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
