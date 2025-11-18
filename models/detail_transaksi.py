from extensions import db

class DetailTransaksi(db.Model):
    id_detail = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_transaksi = db.Column(db.Integer, db.ForeignKey("transaksi.id_transaksi"))
    id_sayur = db.Column(db.Integer, db.ForeignKey("sayur.id_sayur"))
    jumlah = db.Column(db.Integer)
    harga_satuan = db.Column(db.Integer)
    subtotal = db.Column(db.Integer)
