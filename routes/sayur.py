from flask import Blueprint, request, jsonify
from extensions import db
from models.sayur import Sayur
from flask_jwt_extended import jwt_required

sayur_bp = Blueprint("sayur", __name__)

@sayur_bp.post("/add")
@jwt_required()
def add_sayur():
    data = request.json

    sayur = Sayur(
        nama_sayur=data["nama_sayur"],
        harga=data["harga"],
        stok=data["stok"],
        deskripsi=data.get("deskripsi", ""),
        gambar=data.get("gambar", "")
    )

    db.session.add(sayur)
    db.session.commit()

    return jsonify({"message": "Sayur berhasil ditambahkan"})
