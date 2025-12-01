from flask import Blueprint, request, jsonify
from extensions import db
from models.vegetables import Vegetables
from flask_jwt_extended import jwt_required, get_jwt_identity

vegetable_bp = Blueprint("vegetable", __name__)

@vegetable_bp.post("/add")
@jwt_required()
def add():
    data = request.json

    vegetable = Vegetables(
        name=data["name"],
        description=data.get("description", ""),
        price=data["price"],
        stock=data["stock"],
        image=data.get("image", ""),
        category=data["category"],
        status=data.get("status", "available"),
        created_by=data["created_by"],
        created_at=data.get("created_at")
    )
    vegetable.created_by = get_jwt_identity()

    db.session.add(vegetable)
    db.session.commit()

    return jsonify({"message": "Sayuran berhasil ditambahkan"})

@vegetable_bp.get("/list")
def list():
    vegetables = Vegetables.query.all()
    result = []
    for veg in vegetables:
        result.append({
            "id": veg.id,
            "name": veg.name,
            "description": veg.description,
            "price": str(veg.price),
            "stock": veg.stock,
            "image": veg.image,
            "category": veg.category,
            "status": veg.status,
            "created_by": veg.created_by,
            "created_at": veg.created_at,
            "updated_at": veg.updated_at
        })
    return jsonify(result)

@vegetable_bp.get("/get/<int:id>")
def detail(id):
    veg = Vegetables.query.get_or_404(id)
    result = {
        "id": veg.id,
        "name": veg.name,
        "description": veg.description,
        "price": str(veg.price),
        "stock": veg.stock,
        "image": veg.image,
        "category": veg.category,
        "status": veg.status,
        "created_by": veg.created_by,
        "created_at": veg.created_at,
        "updated_at": veg.updated_at
    }
    return jsonify(result)

@vegetable_bp.put("/update/<int:id>")
@jwt_required()
def update(id):
    veg = Vegetables.query.get_or_404(id)
    data = request.json

    veg.name = data.get("name", veg.name)
    veg.description = data.get("description", veg.description)
    veg.price = data.get("price", veg.price)
    veg.stock = data.get("stock", veg.stock)
    veg.image = data.get("image", veg.image)
    veg.category = data.get("category", veg.category)
    veg.status = data.get("status", veg.status)

    db.session.commit()

    return jsonify({"message": "Sayuran berhasil diperbarui"})

@vegetable_bp.delete("/delete/<int:id>")
@jwt_required()
def delete(id):
    veg = Vegetables.query.get_or_404(id)
    db.session.delete(veg)
    db.session.commit()
    return jsonify({"message": "Sayuran berhasil dihapus"})