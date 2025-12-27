import pytest
from flask import Flask
from flask_jwt_extended import JWTManager
from routes.auth import auth_bp
from routes.finance import finance_bp
from routes.transaction import transaction_bp
from routes.vegetable import vegetable_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"

    JWTManager(app)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(transaction_bp, url_prefix="/transaction")
    app.register_blueprint(vegetable_bp, url_prefix="/vegetable")

    return app

@pytest.fixture
def client(app):
    return app.test_client()
