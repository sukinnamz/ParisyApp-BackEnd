from flask import Flask
from config import Config
from extensions import db
from models import Users, Vegetables, Transactions, DetailTransactions
from werkzeug.security import generate_password_hash
from datetime import datetime
from decimal import Decimal

def seed():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Drop
        DetailTransactions.query.delete()
        Transactions.query.delete()
        Vegetables.query.delete()
        Users.query.delete()
        db.session.commit()
        
        # Seed Users
        users = [
            Users(
                name="Admin Utama",
                email="admin@parisy.com",
                password=generate_password_hash("admin123"),
                role="admin",
                sub_role="rw",
                address="Jl. Raya No. 1",
                phone="081234567890"
            ),
            Users(
                name="Sekretaris",
                email="sekretaris@parisy.com",
                password=generate_password_hash("sekretaris123"),
                role="admin",
                sub_role="sekretaris",
                address="Jl. Raya No. 2",
                phone="081234567891"
            ),
            Users(
                name="Bendahara",
                email="bendahara@parisy.com",
                password=generate_password_hash("bendahara123"),
                role="admin",
                sub_role="bendahara",
                address="Jl. Raya No. 2",
                phone="081234567891"
            ),
            Users(
                name="Ketua RT 01",
                email="rt@parisy.com",
                password=generate_password_hash("rt1234"),
                role="user",
                sub_role="rt",
                address="Jl. Mawar No. 5",
                phone="081234567892"
            ),
            Users(
                name="Ketua RW",
                email="rw@parisy.com",
                password=generate_password_hash("rw1234"),
                role="user",
                sub_role="rw",
                address="Jl. Mawar No. 5",
                phone="081234567892"
            ),
            Users(
                name="Budi Santoso",
                email="budi@gmail.com",
                password=generate_password_hash("budi123"),
                role="user",
                sub_role="warga",
                address="Jl. Melati No. 10",
                phone="081234567893"
            )
        ]
        
        db.session.add_all(users)
        db.session.commit()
        print(f"✓ {len(users)} users berhasil ditambahkan")
        
        # Seed Vegetables
        vegetables = [
            Vegetables(
                name="Kangkung",
                description="Kangkung segar dari petani lokal",
                price=Decimal("5000.00"),
                stock=100,
                image="kangkung.jpg",
                category="daun",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Bayam",
                description="Bayam hijau organik",
                price=Decimal("6000.00"),
                stock=80,
                image="bayam.jpg",
                category="daun",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Sawi Hijau",
                description="Sawi hijau segar",
                price=Decimal("4500.00"),
                stock=60,
                image="sawi.jpg",
                category="daun",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Selada",
                description="Selada keriting segar",
                price=Decimal("8000.00"),
                stock=40,
                image="selada.jpg",
                category="daun",
                status="available",
                created_by=users[1].id
            ),
            Vegetables(
                name="Wortel",
                description="Wortel manis kualitas premium",
                price=Decimal("12000.00"),
                stock=50,
                image="wortel.jpg",
                category="akar",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Kentang",
                description="Kentang grade A",
                price=Decimal("15000.00"),
                stock=70,
                image="kentang.jpg",
                category="akar",
                status="available",
                created_by=users[1].id
            ),
            Vegetables(
                name="Bawang Merah",
                description="Bawang merah lokal",
                price=Decimal("35000.00"),
                stock=30,
                image="bawang_merah.jpg",
                category="akar",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Brokoli",
                description="Brokoli hijau segar",
                price=Decimal("18000.00"),
                stock=25,
                image="brokoli.jpg",
                category="bunga",
                status="available",
                created_by=users[1].id
            ),
            Vegetables(
                name="Kembang Kol",
                description="Kembang kol putih segar",
                price=Decimal("16000.00"),
                stock=20,
                image="kembang_kol.jpg",
                category="bunga",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Tomat",
                description="Tomat merah segar",
                price=Decimal("10000.00"),
                stock=90,
                image="tomat.jpg",
                category="buah",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Terong",
                description="Terong ungu berkualitas",
                price=Decimal("7000.00"),
                stock=55,
                image="terong.jpg",
                category="buah",
                status="available",
                created_by=users[1].id
            ),
            Vegetables(
                name="Cabai Merah",
                description="Cabai merah pedas",
                price=Decimal("45000.00"),
                stock=15,
                image="cabai.jpg",
                category="buah",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Buncis",
                description="Buncis segar (stok habis)",
                price=Decimal("9000.00"),
                stock=0,
                image="buncis.jpg",
                category="buah",
                status="unavailable",
                created_by=users[1].id
            ),
        ]
        
        db.session.add_all(vegetables)
        db.session.commit()
        print(f"✓ {len(vegetables)} sayuran berhasil ditambahkan")
        
        # Seed Transactions
        transactions = [
            Transactions(
                code="TRX20250101001",
                user_id=users[3].id, 
                total_price=Decimal("44000.00"),
                payment_method="transfer",
                transaction_status="completed",
                notes="Pesanan untuk acara RT"
            ),
            Transactions(
                code="TRX20250101002",
                user_id=users[4].id,  
                total_price=Decimal("85000.00"),
                payment_method="cash",
                transaction_status="completed",
                notes=None
            ),
            Transactions(
                code="TRX20250101003",
                user_id=users[3].id,  
                total_price=Decimal("62000.00"),
                payment_method="transfer",
                transaction_status="pending",
                notes="Mohon diantar sore"
            ),
            Transactions(
                code="TRX20250101004",
                user_id=users[2].id, 
                total_price=Decimal("150000.00"),
                payment_method="transfer",
                transaction_status="completed",
                notes="Untuk kegiatan posyandu"
            ),
            Transactions(
                code="TRX20250101005",
                user_id=users[4].id,  
                total_price=Decimal("28000.00"),
                payment_method="cash",
                transaction_status="cancelled",
                notes="Dibatalkan karena barang tidak sesuai"
            ),
        ]
        
        db.session.add_all(transactions)
        db.session.commit()
        print(f"✓ {len(transactions)} transaksi berhasil ditambahkan")
        
        # Seed Detail Transactions
        detail_transactions = [
            DetailTransactions(
                transaction_id=transactions[0].id,
                vegetable_id=vegetables[0].id,
                quantity=3,
                unit_price=Decimal("5000.00"),
                subtotal=Decimal("15000.00")
            ),
            DetailTransactions(
                transaction_id=transactions[0].id,
                vegetable_id=vegetables[1].id,
                quantity=2,
                unit_price=Decimal("6000.00"),
                subtotal=Decimal("12000.00")
            ),
            DetailTransactions(
                transaction_id=transactions[0].id,
                vegetable_id=vegetables[9].id,
                quantity=1,
                unit_price=Decimal("10000.00"),
                subtotal=Decimal("10000.00")
            ),
            DetailTransactions(
                transaction_id=transactions[0].id,
                vegetable_id=vegetables[10].id,
                quantity=1,
                unit_price=Decimal("7000.00"),
                subtotal=Decimal("7000.00")
            ),
            DetailTransactions(
                transaction_id=transactions[1].id,
                vegetable_id=vegetables[6].id,  
                quantity=2,
                unit_price=Decimal("35000.00"),
                subtotal=Decimal("70000.00")
            ),
            DetailTransactions(
                transaction_id=transactions[1].id,
                vegetable_id=vegetables[5].id, 
                quantity=1,
                unit_price=Decimal("15000.00"),
                subtotal=Decimal("15000.00")
            ),
            DetailTransactions(
                transaction_id=transactions[2].id,
                vegetable_id=vegetables[7].id, 
                quantity=2,
                unit_price=Decimal("18000.00"),
                subtotal=Decimal("36000.00")
            ),
            DetailTransactions(
                transaction_id=transactions[2].id,
                vegetable_id=vegetables[4].id, 
                quantity=2,
                unit_price=Decimal("12000.00"),
                subtotal=Decimal("24000.00")
            ),
            DetailTransactions(
                transaction_id=transactions[2].id,
                vegetable_id=vegetables[2].id, 
                quantity=1,
                unit_price=Decimal("4500.00"),
                subtotal=Decimal("4500.00")
            ),
            DetailTransactions(
                transaction_id=transactions[3].id,
                vegetable_id=vegetables[0].id,  
                quantity=10,
                unit_price=Decimal("5000.00"),
                subtotal=Decimal("50000.00")
            ),
            DetailTransactions(
                transaction_id=transactions[3].id,
                vegetable_id=vegetables[1].id,  
                quantity=8,
                unit_price=Decimal("6000.00"),
                subtotal=Decimal("48000.00")
            ),
            DetailTransactions(
                transaction_id=transactions[3].id,
                vegetable_id=vegetables[9].id,  
                quantity=5,
                unit_price=Decimal("10000.00"),
                subtotal=Decimal("50000.00")
            ),
            DetailTransactions(
                transaction_id=transactions[4].id,
                vegetable_id=vegetables[3].id,  
                quantity=2,
                unit_price=Decimal("8000.00"),
                subtotal=Decimal("16000.00")
            ),
            DetailTransactions(
                transaction_id=transactions[4].id,
                vegetable_id=vegetables[4].id,  
                quantity=1,
                unit_price=Decimal("12000.00"),
                subtotal=Decimal("12000.00")
            ),
        ]
        
        db.session.add_all(detail_transactions)
        db.session.commit()
        print(f"✓ {len(detail_transactions)} detail transaksi berhasil ditambahkan")

if __name__ == "__main__":
    seed()
