from faker import Faker
from models.sayur import Sayur
from extensions import db

fake = Faker()

def test_add_sayur(client, token, app):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "nama_sayur": fake.word(),
        "harga": 10000,
        "stok": 20,
        "deskripsi": "Segar",
        "gambar": "url"
    }

    res = client.post("/sayur/add", json=data, headers=headers)
    assert res.status_code == 200

    with app.app_context():
        sayur = Sayur.query.filter_by(nama_sayur=data["nama_sayur"]).first()
        assert sayur is not None
