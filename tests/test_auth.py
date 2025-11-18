from faker import Faker
from models.user import User
from extensions import db
from werkzeug.security import generate_password_hash

fake = Faker()


def test_register(client, app):
    data = {
        "nama": fake.name(),
        "email": fake.email(),
        "password": "123456",
        "alamat": fake.address(),
        "no_hp": "08123"
    }

    res = client.post("/auth/register", json=data)
    assert res.status_code == 200
    assert "Registrasi berhasil" in res.json["message"]

    with app.app_context():
        user = User.query.filter_by(email=data["email"]).first()
        assert user is not None


def test_login_success(client, app):
    # buat user dengan password hashed
    hashed = generate_password_hash("password123")

    with app.app_context():
        user = User(
            nama="Test User",
            email="test@example.com",
            password=hashed
        )
        db.session.add(user)
        db.session.commit()

    # login dengan email yang benar
    res = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })

    assert res.status_code == 200
    assert "token" in res.json


def test_login_fail(client):
    res = client.post("/auth/login", json={
        "email": fake.email(),
        "password": "wrong"
    })

    assert res.status_code == 401
