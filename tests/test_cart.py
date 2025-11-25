from models.sayur import Sayur
from models.user import User
from extensions import db

def test_add_to_cart(client, token, app):
    headers = {"Authorization": f"Bearer {token}"}

    with app.app_context():
        sayur = Sayur(nama_sayur="Bayam", harga=5000, stok=20)
        user = User(nama="u", email="u@mail.com", password="x")
        db.session.add_all([sayur, user])
        db.session.commit()

    res = client.post("/cart/add", json={
        "id_sayur": 1,
        "jumlah": 3
    }, headers=headers)

    assert res.status_code == 200
    assert res.json["message"] == "Berhasil memasukkan ke keranjang"

    # Test get cart
    res = client.get("/cart/", headers=headers)
    assert res.status_code == 200
    assert len(res.json["cart"]) == 1
    assert res.json["cart"][0]["id_sayur"] == 1
    assert res.json["cart"][0]["jumlah"] == 3
