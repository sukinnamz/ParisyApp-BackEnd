from faker import Faker
from models.user import User
from extensions import db

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
    # buat user manual
    user = User(
        nama="Test",
        email="test@mail.com",
        password="$pbkdf2-sha256$fakehash",  # bypass hashing
    )
    db.session.add(user)
    db.session.commit()

    # mock check_password_hash supaya selalu true
    res = client.post("/auth/login", json={
        "email": "test@mail.com",
        "password": "abc"
    })

    assert res.status_code == 200
    assert "token" in res.json


def test_login_fail(client):
    res = client.post("/auth/login", json={
        "email": fake.email(),
        "password": "wrong"
    })
    assert res.status_code == 401
