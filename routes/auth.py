from flask import Blueprint, request, jsonify
from extensions import db
from models.users import Users
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint("auth", __name__)

def user_data(user, data_full=False):
    data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "password": user.password,
        "role": user.role,
        "sub_role": user.sub_role
    }
    if data_full:
        data.update({
            "address": user.address,
            "phone": user.phone,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        })
    return data

@auth_bp.post("/register")
def register():
    data = request.get_json()

    if Users.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email sudah terdaftar"}), 409
    
    hashed = generate_password_hash(data["password"])

    user = Users(
        name=data["name"],
        email=data["email"],
        password=hashed,
        address=data.get("address", ""),
        phone=data.get("phone", ""),
        role=data.get("role", ""),
        sub_role=data.get("sub_role", "")
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registrasi berhasil",}), 201

@auth_bp.post("/login")
def login():
    data = request.get_json()
    user = Users.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"message": "Email atau password salah"}), 401

    return jsonify({
        "message": "Login berhasil",
        "token": create_access_token(identity=str(user.id)),
        "user": user_data(user)
    }), 200

@auth_bp.get("/logout")
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    user = Users.query.get_or_404(int(user_id))
    return jsonify({
        "message": "Logout berhasil",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }), 200

@auth_bp.get("/profile/<int:id>")
@jwt_required()
def profile(id):
    user = Users.query.get_or_404(id)
    return jsonify(user_data(user, data_full=True)), 200

@auth_bp.get("/all")
@jwt_required()
def all_users():
    users = Users.query.all()
    return jsonify([user_data(user) for user in users]), 200

@auth_bp.put("/edit/<int:id>")
@jwt_required()
def edit(id):
    data = request.get_json()
    user = Users.query.get_or_404(id)

    user.name = data.get("name", user.name)
    user.address = data.get("address", user.address)
    user.phone = data.get("phone", user.phone)

    if data.get("password"):
        user.password = generate_password_hash(data["password"])

    db.session.commit()
    return jsonify({"message": "Profil berhasil diperbarui"}), 200
    
@auth_bp.delete("/delete/<int:id>")
@jwt_required()
def delete(id):
    user = Users.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Akun berhasil dihapus"}), 200