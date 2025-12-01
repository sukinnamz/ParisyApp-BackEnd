from models.sayur import Sayur
from models.user import User
from models.transaksi import Transaksi
from extensions import db

def test_checkout(client, token, app):
    headers = {"Authorization": f"Bearer {token}"}

    with app.app_context():
        sayur = Sayur(nama_sayur="Tomat", harga=5000, stok=10)
        db.session.add(sayur)
        db.session.commit()
        sayur_id = sayur.id_sayur

    # Add item to cart first using session
    client.post("/cart/add", json={
        "id_sayur": sayur_id,
        "jumlah": 2
    }, headers=headers)

    # Now checkout
    res = client.post("/transaksi/checkout",
                      json={"metode_pembayaran": "COD"},
                      headers=headers)

    assert res.status_code == 200
    assert res.json["message"] == "Checkout berhasil"
