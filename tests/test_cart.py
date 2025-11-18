from models.keranjang import Keranjang
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

    with app.app_context():
        cart = Keranjang.query.filter_by(id_sayur=1).first()
        assert cart is not None
        assert cart.jumlah == 3
