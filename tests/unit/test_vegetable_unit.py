import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from routes.vegetable import vegetable_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"
    JWTManager(app)
    app.register_blueprint(vegetable_bp, url_prefix="/vegetable")
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity="1")
    return {"Authorization": f"Bearer {token}"}


# =========================
# ADD VEGETABLE (FIX)
# =========================
@patch("routes.vegetable.vegetable_data")
@patch("routes.vegetable.db.session")
@patch("routes.vegetable.predict_category_from_image")
@patch("routes.vegetable.Vegetables")
@patch("routes.vegetable.Users")
def test_add_vegetable_success(
    mock_user,
    mock_veg,
    mock_predict,
    mock_session,
    mock_serializer,
    client,
    app
):
    user = MagicMock()
    user.id = 1
    user.sub_role = "admin"

    mock_user.query.get_or_404.return_value = user
    mock_veg.query.filter_by.return_value.first.return_value = None
    mock_predict.return_value = "daun"

    # 🔥 PENTING: serializer dipaksa return dict
    mock_serializer.return_value = {
        "id": 1,
        "name": "Bayam",
        "price": "1000",
        "stock": 0,
        "category": "daun"
    }

    res = client.post(
        "/vegetable/add",
        json={
            "name": "Bayam",
            "price": 1000,
            "image": "http://img"
        },
        headers=auth_headers(app)
    )

    assert res.status_code == 201
    assert res.json["vegetable"]["name"] == "Bayam"
