from models.keranjang import Keranjang
from models.sayur import Sayur
from models.user import User
from models.transaksi import Transaksi
from extensions import db

def test_checkout(client, token, app):
    from models.sayur import Sayur
    from models.keranjang import Keranjang
    from extensions import db

    with app.app_context():
        sayur = Sayur(nama_sayur="Tomat", harga=5000, stok=10)
        db.session.add(sayur)
        db.session.commit()

        cart = Keranjang(id_user=1, id_sayur=sayur.id_sayur, jumlah=2)
        db.session.add(cart)
        db.session.commit()

    res = client.post("/transaksi/checkout",
                      json={"metode_pembayaran": "COD"},
                      headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 200
