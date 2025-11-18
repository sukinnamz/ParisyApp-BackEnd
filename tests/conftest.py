import pytest
from app import create_app
from extensions import db
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
from models.user import User


@pytest.fixture
def app():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True

    # FIX PENTING
    app.config["JWT_SECRET_KEY"] = "test-secret"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_COOKIE_SECURE"] = False
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def token(app):
    with app.app_context():
        user = User(
            nama="Test User",
            email="jwt@test.com",
            password=generate_password_hash("password")
        )
        db.session.add(user)
        db.session.commit()

        jwt_token = create_access_token(identity=str(user.id_user))
        return jwt_token
