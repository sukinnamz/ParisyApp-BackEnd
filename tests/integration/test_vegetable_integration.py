import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from extensions import db
from routes.vegetable import vegetable_bp
from models.vegetables import Vegetables
from models.users import Users


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    JWTManager(app)
    app.register_blueprint(vegetable_bp, url_prefix="/vegetable")

    with app.app_context():
        db.create_all()

        # 🔥 USERS WAJIB LENGKAP
        user = Users(
            id=1,
            name="Admin Test",
            email="admin@test.com",
            password="hashed-password",
            role="admin",
            sub_role="admin"
        )

        veg = Vegetables(
            name="Bayam",
            description="Hijau",
            price=1000,
            stock=10,
            category="daun",
            status="available",
            created_by=1
        )

        db.session.add(user)
        db.session.add(veg)
        db.session.commit()

    return app


@pytest.fixture
def client(app):
    return app.test_client()


def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity="1")
    return {"Authorization": f"Bearer {token}"}


# =========================
# LIST
# =========================
def test_list_vegetables_integration(client):
    res = client.get("/vegetable/list")
    assert res.status_code == 200
    assert len(res.json) == 1


# =========================
# DETAIL
# =========================
def test_detail_vegetable(client):
    res = client.get("/vegetable/get/1")
    assert res.status_code == 200
    assert res.json["name"] == "Bayam"


# =========================
# UPDATE STOCK
# =========================
def test_update_stock_integration(client, app):
    res = client.put(
        "/vegetable/update-stock/1",
        json={"stock": 20},
        headers=auth_headers(app)
    )
    assert res.status_code == 200
    assert res.json["vegetable"]["stock"] == 20


# =========================
# DELETE
# =========================
def test_delete_vegetable(client, app):
    res = client.delete(
        "/vegetable/delete/1",
        headers=auth_headers(app)
    )
    assert res.status_code == 200
