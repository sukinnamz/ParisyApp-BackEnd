import pytest
import os
import sys
from flask import Flask
from flask_jwt_extended import JWTManager

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, BASE_DIR)

from routes.auth import auth_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "testing-secret"

    JWTManager(app)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    return app

@pytest.fixture
def client(app):
    return app.test_client()
