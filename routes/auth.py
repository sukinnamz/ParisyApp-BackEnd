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
    
    current_user_id = get_jwt_identity()
    current_user = Users.query.get(current_user_id)
    
    if str(current_user_id) != str(id) and current_user.role not in ['admin', 'rw'] and current_user.sub_role != 'rt':
        return jsonify({"message": "Unauthorized"}), 403
    
    return jsonify(user_data(user, data_full=True)), 200

@auth_bp.get("/all")
@jwt_required()
def all_users():
    current_user_id = get_jwt_identity()
    current_user = Users.query.get(current_user_id)
    
    if current_user.sub_role == 'admin':
        users = Users.query.all()
    elif current_user.sub_role == 'rw':
        users = Users.query.filter(
            Users.sub_role.in_(['warga', 'rt', 'rw'])
        ).all()
    elif current_user.sub_role == 'rt':
        users = Users.query.filter_by(sub_role='warga').all()
    else:
        return jsonify({"message": "Unauthorized"}), 403
    
    return jsonify([user_data(user, data_full=True) for user in users]), 200

@auth_bp.put("/edit/<int:id>")
@jwt_required()
def edit(id):
    data = request.get_json()
    user = Users.query.get_or_404(id)
    
    current_user_id = get_jwt_identity()
    current_user = Users.query.get(current_user_id)
    
    if str(current_user_id) != str(id) and current_user.sub_role != 'admin':
        return jsonify({"message": "Hanya admin yang dapat mengedit pengguna lain"}), 403
    
    if "name" in data:
        user.name = data["name"]
    if "email" in data:
        existing_user = Users.query.filter_by(email=data["email"]).first()
        if existing_user and existing_user.id != id:
            return jsonify({"message": "Email sudah digunakan"}), 409
        user.email = data["email"]
    if "address" in data:
        user.address = data["address"]
    if "phone" in data:
        user.phone = data["phone"]
    if "password" in data and data["password"]:
        user.password = generate_password_hash(data["password"])
    if "role" in data and current_user.sub_role == 'admin':
        user.role = data["role"]
    if "sub_role" in data and current_user.sub_role == 'admin':
        user.sub_role = data["sub_role"]
    
    db.session.commit()
    return jsonify({
        "message": "Profil berhasil diperbarui",
        "user": user_data(user)
    }), 200
    
@auth_bp.delete("/delete/<int:id>")
@jwt_required()
def delete(id):
    user = Users.query.get_or_404(id)
    
    current_user_id = get_jwt_identity()
    current_user = Users.query.get(current_user_id)
    
    if current_user.sub_role != 'admin':
        return jsonify({"message": "Hanya admin yang dapat menghapus pengguna"}), 403
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Akun berhasil dihapus"}), 200