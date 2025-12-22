from flask import Flask
from config import Config
from extensions import db, jwt
from models import *
from routes import auth_bp, vegetable_bp, transaction_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"], 
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"]
        }
    })

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(sayur_bp, url_prefix="/sayur")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(transaksi_bp, url_prefix="/transaksi")

    with app.app_context():
        db.create_all()

    return app

