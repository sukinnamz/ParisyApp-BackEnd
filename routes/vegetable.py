from flask import Blueprint, request, jsonify
from extensions import db
from models.vegetables import Vegetables
from models.users import Users
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from functools import wraps

vegetable_bp = Blueprint("vegetable", __name__)

def get_current_user():
    return Users.query.get_or_404(int(get_jwt_identity()))

def requires_permission(permission_check, error_msg="Anda tidak memiliki izin"):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            if not permission_check(current_user):
                return jsonify({"message": error_msg}), 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

def can_manage_vegetables(user):
    return user.sub_role in ['admin', 'rw', 'rt']

def can_update_stock(user):
    return user.sub_role in ['admin', 'sekretaris']

def can_view_admin(user):
    return user.role == 'admin' or user.sub_role in ['rw', 'rt', 'sekretaris', 'bendahara']

def vegetable_data(vegetable, detailed=False):
    data = {
        "id": vegetable.id,
        "name": vegetable.name,
        "description": vegetable.description or "",
        "price": str(vegetable.price),
        "stock": vegetable.stock,
        "image": vegetable.image or "",
        "category": vegetable.category,
        "status": vegetable.status,
        "created_by": vegetable.created_by,
    }
    
    if detailed:
        data.update({
            "created_at": vegetable.created_at.isoformat() if vegetable.created_at else None,
            "updated_at": vegetable.updated_at.isoformat() if vegetable.updated_at else None,
        })
    
    return data

@vegetable_bp.get("/list")
def list_vegetables():
    vegetables = Vegetables.query.filter_by(status="available").all()
    
    vegetables.sort(key=lambda x: (0 if x.status == "available" else 1, x.name))
    
    return jsonify([vegetable_data(veg) for veg in vegetables]), 200

@vegetable_bp.get("/get/<int:id>")
def detail(id):
    veg = Vegetables.query.get_or_404(id)
    return jsonify(vegetable_data(veg, detailed=True)), 200

@vegetable_bp.get("/by-category/<string:category>")
def by_category(category):
    vegetables = Vegetables.query.filter_by(
        category=category, 
        status="available"
    ).all()
    return jsonify([vegetable_data(veg) for veg in vegetables]), 200

@vegetable_bp.post("/add")
@requires_permission(can_manage_vegetables, "Anda tidak memiliki izin untuk menambah sayuran")
def add(current_user):
    data = request.get_json()
    
    if not data.get("name") or not data.get("price"):
        return jsonify({"message": "Nama sayuran dan harga harus diisi"}), 400
    
    if Vegetables.query.filter_by(name=data["name"]).first():
        return jsonify({"message": "Sayuran dengan nama tersebut sudah ada"}), 409
    
    vegetable = Vegetables(
        name=data["name"],
        description=data.get("description", ""),
        price=float(data["price"]),
        stock=int(data.get("stock", 0)),
        image=data.get("image", ""),
        category=data.get("category", "sayuran"),
        status=data.get("status", "available"),
        created_by=current_user.id
    )

    db.session.add(vegetable)
    db.session.commit()

    return jsonify({
        "message": "Sayuran berhasil ditambahkan",
        "vegetable": vegetable_data(vegetable)
    }), 201

@vegetable_bp.put("/update/<int:id>")
@requires_permission(can_manage_vegetables, "Anda tidak memiliki izin untuk mengupdate sayuran")
def update(current_user, id):
    veg = Vegetables.query.get_or_404(id)
    data = request.get_json()
    
    for field in ['name', 'description', 'image', 'category', 'status']:
        if field in data:
            setattr(veg, field, data[field])
    
    if 'price' in data:
        veg.price = float(data['price'])
    
    if 'stock' in data:
        if not can_update_stock(current_user):
            return jsonify({"message": "Anda tidak memiliki izin untuk mengupdate stok"}), 403
        veg.stock = int(data['stock'])
    
    veg.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "message": "Sayuran berhasil diperbarui",
        "vegetable": vegetable_data(veg)
    }), 200

@vegetable_bp.delete("/delete/<int:id>")
@requires_permission(can_manage_vegetables, "Anda tidak memiliki izin untuk menghapus sayuran")
def delete(current_user, id):
    veg = Vegetables.query.get_or_404(id)
    db.session.delete(veg)
    db.session.commit()
    return jsonify({"message": "Sayuran berhasil dihapus"}), 200

@vegetable_bp.get("/admin/list")
@requires_permission(can_view_admin, "Unauthorized")
def admin_list(current_user):
    vegetables = sorted(
        Vegetables.query.all(),
        key=lambda x: (x.status != "available", x.name)
    )
    return jsonify([vegetable_data(veg, detailed=True) for veg in vegetables]), 200

@vegetable_bp.put("/update-stock/<int:id>")
@requires_permission(can_update_stock, "Hanya admin dan sekretaris yang dapat mengupdate stok")
def update_stock(current_user, id):
    veg = Vegetables.query.get_or_404(id)
    data = request.get_json()
    
    if "stock" not in data:
        return jsonify({"message": "Stock harus diisi"}), 400
    
    veg.stock = int(data["stock"])
    veg.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "message": "Stok berhasil diperbarui",
        "vegetable": vegetable_data(veg)
    }), 200

@vegetable_bp.put("/update-status/<int:id>")
@requires_permission(can_manage_vegetables, "Anda tidak memiliki izin untuk mengupdate status")
def update_status(current_user, id):
    veg = Vegetables.query.get_or_404(id)
    data = request.get_json()
    
    if "status" not in data or data["status"] not in ["available", "unavailable"]:
        return jsonify({"message": "Status harus 'available' atau 'unavailable'"}), 400
    
    veg.status = data["status"]
    veg.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "message": "Status berhasil diperbarui",
        "vegetable": vegetable_data(veg)
    }), 200

@vegetable_bp.get("/search")
def search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    vegetables = Vegetables.query.filter_by(status="available")
    
    if query:
        vegetables = vegetables.filter(
            (Vegetables.name.ilike(f"%{query}%")) |
            (Vegetables.description.ilike(f"%{query}%"))
        )
    
    if category:
        vegetables = vegetables.filter_by(category=category)
    
    vegetables = vegetables.all()
    vegetables.sort(key=lambda x: x.name)
    
    return jsonify([vegetable_data(veg) for veg in vegetables]), 200