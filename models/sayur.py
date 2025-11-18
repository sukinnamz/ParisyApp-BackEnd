from extensions import db
from datetime import datetime

class Sayur(db.Model):
    id_sayur = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_sayur = db.Column(db.String(100))
    harga = db.Column(db.Integer)
    stok = db.Column(db.Integer)
    deskripsi = db.Column(db.Text)
    gambar = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
