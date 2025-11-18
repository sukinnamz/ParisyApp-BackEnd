from flask import Blueprint, request, jsonify
from extensions import db
from models.keranjang import Keranjang
from flask_jwt_extended import jwt_required, get_jwt_identity

cart_bp = Blueprint("cart", __name__)

@cart_bp.post("/add")
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.json

    cart = Keranjang(
        id_user=user_id,
        id_sayur=data["id_sayur"],
        jumlah=data["jumlah"]
    )

    db.session.add(cart)
    db.session.commit()

    return jsonify({"message": "Berhasil memasukkan ke keranjang"})
