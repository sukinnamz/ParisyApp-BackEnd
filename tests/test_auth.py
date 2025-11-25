from faker import Faker
from models.user import User
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

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


def test_get_profile(client, app, token):
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/auth/profile", headers=headers)

    assert res.status_code == 200
    assert res.json["nama"] == "Test User"
    assert res.json["email"] == "jwt@test.com"
    assert "id_user" in res.json
    assert "created_at" in res.json


def test_get_profile_unauthorized(client):
    res = client.get("/auth/profile")
    assert res.status_code == 401


def test_edit_user_nama(client, app, token):
    headers = {"Authorization": f"Bearer {token}"}
    new_data = {
        "nama": "Updated Name"
    }

    res = client.put("/auth/edit", json=new_data, headers=headers)

    assert res.status_code == 200
    assert "Profil berhasil diperbarui" in res.json["message"]
    assert res.json["user"]["nama"] == "Updated Name"

    with app.app_context():
        user = User.query.filter_by(email="jwt@test.com").first()
        assert user.nama == "Updated Name"


def test_edit_user_alamat(client, app, token):
    headers = {"Authorization": f"Bearer {token}"}
    new_alamat = "Jalan Merdeka No. 123"

    res = client.put("/auth/edit", json={"alamat": new_alamat}, headers=headers)

    assert res.status_code == 200
    assert res.json["user"]["alamat"] == new_alamat


def test_edit_user_no_hp(client, app, token):
    headers = {"Authorization": f"Bearer {token}"}
    new_no_hp = "081234567890"

    res = client.put("/auth/edit", json={"no_hp": new_no_hp}, headers=headers)

    assert res.status_code == 200
    assert res.json["user"]["no_hp"] == new_no_hp


def test_edit_user_password(client, app, token):
    headers = {"Authorization": f"Bearer {token}"}
    new_password = "newpassword123"

    res = client.put("/auth/edit", json={"password": new_password}, headers=headers)

    assert res.status_code == 200
    assert "Profil berhasil diperbarui" in res.json["message"]

    with app.app_context():
        user = User.query.filter_by(email="jwt@test.com").first()
        assert check_password_hash(user.password, new_password)


def test_edit_user_multiple_fields(client, app, token):
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "nama": "New Name",
        "alamat": "Jalan Baru 456",
        "no_hp": "082111111111",
        "password": "newpass123"
    }

    res = client.put("/auth/edit", json=update_data, headers=headers)

    assert res.status_code == 200
    assert res.json["user"]["nama"] == "New Name"
    assert res.json["user"]["alamat"] == "Jalan Baru 456"
    assert res.json["user"]["no_hp"] == "082111111111"

    with app.app_context():
        user = User.query.filter_by(email="jwt@test.com").first()
        assert user.nama == "New Name"
        assert check_password_hash(user.password, "newpass123")


def test_edit_user_unauthorized(client):
    res = client.put("/auth/edit", json={"nama": "New Name"})
    assert res.status_code == 401


def test_delete_user(client, app, token):
    headers = {"Authorization": f"Bearer {token}"}

    with app.app_context():
        user = User.query.filter_by(email="jwt@test.com").first()
        user_id = user.id_user

    res = client.delete("/auth/delete", headers=headers)

    assert res.status_code == 200
    assert "Akun berhasil dihapus" in res.json["message"]

    with app.app_context():
        user = db.session.get(User, user_id)
        assert user is None


def test_delete_user_unauthorized(client):
    res = client.delete("/auth/delete")
    assert res.status_code == 401
