from flask import Flask
from config import Config
from extensions import db, jwt
from models import *
from routes import transaction_bp, detail_transaction_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(transaction_bp, url_prefix="/transaction")
    app.register_blueprint(detail_transaction_bp, url_prefix="/detail-transaction")

    with app.app_context():
        db.create_all()

    return app
