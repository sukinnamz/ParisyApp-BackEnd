from extensions import db
from datetime import datetime

class Transaksi(db.Model):
    id_transaksi = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer, db.ForeignKey("user.id_user"))
    total_harga = db.Column(db.Integer)
    tanggal_transaksi = db.Column(db.DateTime, default=datetime.utcnow)
    metode_pembayaran = db.Column(db.String(100))
    status_transaksi = db.Column(db.String(100))
    alamat_pengiriman = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
