from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity

cart_bp = Blueprint("cart", __name__)

@cart_bp.post("/add")
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.json
    
    # Initialize cart in session if not exists
    if 'cart' not in session:
        session['cart'] = {}
    
    # Get cart for current user
    user_cart_key = str(user_id)
    if user_cart_key not in session['cart']:
        session['cart'][user_cart_key] = []
    
    # Add item to cart
    cart_item = {
        "id_sayur": data["id_sayur"],
        "jumlah": data["jumlah"]
    }
    
    # Check if item already exists in cart
    existing_item = None
    for item in session['cart'][user_cart_key]:
        if item['id_sayur'] == data["id_sayur"]:
            existing_item = item
            break
    
    if existing_item:
        # Update quantity if item exists
        existing_item['jumlah'] += data["jumlah"]
    else:
        # Add new item to cart
        session['cart'][user_cart_key].append(cart_item)
    
    session.modified = True

    return jsonify({"message": "Berhasil memasukkan ke keranjang"})

@cart_bp.get("/")
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    user_cart_key = str(user_id)
    
    # Get cart items from session
    cart_items = []
    if 'cart' in session and user_cart_key in session['cart']:
        cart_items = session['cart'][user_cart_key]
    
    return jsonify({"cart": cart_items})

@cart_bp.delete("/clear")
@jwt_required()
def clear_cart():
    user_id = get_jwt_identity()
    user_cart_key = str(user_id)
    
    # Clear cart from session
    if 'cart' in session and user_cart_key in session['cart']:
        session['cart'][user_cart_key] = []
        session.modified = True
    
    return jsonify({"message": "Keranjang berhasil dikosongkan"})
