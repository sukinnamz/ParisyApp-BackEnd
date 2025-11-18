from flask import Blueprint, request, jsonify
from extensions import db
from models.keranjang import Keranjang
from models.transaksi import Transaksi
from models.detail_transaksi import DetailTransaksi
from models.sayur import Sayur
from flask_jwt_extended import jwt_required, get_jwt_identity

transaksi_bp = Blueprint("transaksi", __name__)

@transaksi_bp.post("/checkout")
@jwt_required()
def checkout():
    user_id = get_jwt_identity()
    data = request.json

    keranjang_items = Keranjang.query.filter_by(id_user=user_id).all()
    if not keranjang_items:
        return jsonify({"message": "Keranjang kosong"}), 400

    total_harga = 0
    for item in keranjang_items:
        sayur = Sayur.query.get(item.id_sayur)
        total_harga += sayur.harga * item.jumlah

    transaksi = Transaksi(
        id_user=user_id,
        total_harga=total_harga,
        metode_pembayaran=data["metode_pembayaran"],
        status_transaksi="Diproses",
        alamat_pengiriman=data.get("alamat_pengiriman", "")
    )
    db.session.add(transaksi)
    db.session.commit()

    for item in keranjang_items:
        sayur = Sayur.query.get(item.id_sayur)

        detail = DetailTransaksi(
            id_transaksi=transaksi.id_transaksi,
            id_sayur=item.id_sayur,
            jumlah=item.jumlah,
            harga_satuan=sayur.harga,
            subtotal=sayur.harga * item.jumlah
        )
        db.session.add(detail)

        sayur.stok -= item.jumlah

    Keranjang.query.filter_by(id_user=user_id).delete()
    db.session.commit()

    return jsonify({"message": "Checkout berhasil", "id_transaksi": transaksi.id_transaksi})
