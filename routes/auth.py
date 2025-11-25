from flask import Blueprint, request, jsonify
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

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


@auth_bp.get("/profile")
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User tidak ditemukan"}), 404

    return jsonify({
        "id_user": user.id_user,
        "nama": user.nama,
        "email": user.email,
        "alamat": user.alamat,
        "no_hp": user.no_hp,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    })


@auth_bp.put("/edit")
@jwt_required()
def edit_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User tidak ditemukan"}), 404

    data = request.json

    if "nama" in data:
        user.nama = data["nama"]
    if "alamat" in data:
        user.alamat = data["alamat"]
    if "no_hp" in data:
        user.no_hp = data["no_hp"]
    if "password" in data:
        user.password = generate_password_hash(data["password"])

    db.session.commit()

    return jsonify({
        "message": "Profil berhasil diperbarui",
        "user": {
            "id_user": user.id_user,
            "nama": user.nama,
            "email": user.email,
            "alamat": user.alamat,
            "no_hp": user.no_hp,
            "updated_at": user.updated_at
        }
    })


@auth_bp.delete("/delete")
@jwt_required()
def delete_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User tidak ditemukan"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "Akun berhasil dihapus"})
