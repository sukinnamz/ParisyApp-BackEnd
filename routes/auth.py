from flask import Blueprint, request, jsonify
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    data = request.json
    hashed = generate_password_hash(data["password"])

    user = User(
        nama=data["nama"],
        email=data["email"],
        password=hashed,
        alamat=data.get("alamat", ""),
        no_hp=data.get("no_hp", "")
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registrasi berhasil"})


@auth_bp.post("/login")
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"message": "Email atau password salah"}), 401

    token = create_access_token(identity=user.id_user)
    return jsonify({"token": token})
