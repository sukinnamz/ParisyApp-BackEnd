from models.keranjang import Keranjang
from models.sayur import Sayur
from models.user import User
from models.transaksi import Transaksi
from extensions import db

def test_checkout(client, token, app):
    headers = {"Authorization": f"Bearer {token}"}

    with app.app_context():
        user = User(id_user=1, nama="A", email="a@mail.com", password="x")
        sayur = Sayur(id_sayur=1, nama_sayur="Wortel", harga=2000, stok=10)
        cart = Keranjang(id_user=1, id_sayur=1, jumlah=2)
        
        db.session.add_all([user, sayur, cart])
        db.session.commit()

    res = client.post("/transaksi/checkout", json={
        "metode_pembayaran": "COD",
        "alamat_pengiriman": "Rumah"
    }, headers=headers)

    assert res.status_code == 200
    assert "Checkout berhasil" in res.json["message"]

    with app.app_context():
        trx = Transaksi.query.first()
        assert trx.total_harga == 4000  # 2 * 2000
