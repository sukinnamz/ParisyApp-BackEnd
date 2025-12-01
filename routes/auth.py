from flask import Blueprint, request, jsonify
from extensions import db
from models.users import Users
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    try:
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
            role=data.get("role", "user"),
            sub_role=data.get("sub_role", "warga")
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Registrasi berhasil",}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500


@auth_bp.post("/login")
def login():
    try:
        data = request.get_json()

        user = Users.query.filter_by(email=data["email"]).first()

        if not user or not check_password_hash(user.password, data["password"]):
            return jsonify({"message": "Email atau password salah"}), 401

        token = create_access_token(identity=str(user.id))
        
        return jsonify({
            "message": "Login berhasil",
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "sub_role": user.sub_role
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@auth_bp.get("/profile")
@jwt_required()
def profile():
    try:
        current_user_id = int(get_jwt_identity())
        user = Users.query.get(current_user_id)
        
        if not user:
            return jsonify({"message": "User tidak ditemukan"}), 404
        
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "sub_role": user.sub_role,
            "address": user.address,
            "phone": user.phone,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
