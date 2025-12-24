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
                sub_role="admin",
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
                name="Bawang Bombay",
                description="Bawang bombay segar dari petani lokal",
                price=Decimal("15000.00"),
                stock=50,
                image="https://via.placeholder.com/300x300?text=Bawang+Bombay",
                category="akar",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Wortel",
                description="Wortel organik, kaya akan vitamin A",
                price=Decimal("12000.00"),
                stock=100,
                image="https://via.placeholder.com/300x300?text=Wortel",
                category="akar",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Kentang",
                description="Kentang segar, cocok untuk berbagai masakan",
                price=Decimal("10000.00"),
                stock=80,
                image="https://via.placeholder.com/300x300?text=Kentang",
                category="akar",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Kangkung",
                description="Kangkung segar dari sawah lokal",
                price=Decimal("8000.00"),
                stock=60,
                image="https://via.placeholder.com/300x300?text=Kangkung",
                category="daun",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Kubis",
                description="Kubis segar, kaya serat dan vitamin",
                price=Decimal("9000.00"),
                stock=70,
                image="https://via.placeholder.com/300x300?text=Kubis",
                category="daun",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Sawi Putih",
                description="Sawi putih segar, cocok untuk sayur bening",
                price=Decimal("8500.00"),
                stock=90,
                image="https://via.placeholder.com/300x300?text=Sawi+Putih",
                category="daun",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Tomat",
                description="Tomat segar, kaya akan likopen",
                price=Decimal("7000.00"),
                stock=120,
                image="https://via.placeholder.com/300x300?text=Tomat",
                category="buah",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Timun",
                description="Timun segar, cocok untuk lalapan",
                price=Decimal("6000.00"),
                stock=110,
                image="https://via.placeholder.com/300x300?text=Timun",
                category="buah",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Cabai",
                description="Cabai merah segar, pedas alami",
                price=Decimal("20000.00"),
                stock=40,
                image="https://via.placeholder.com/300x300?text=Cabai",
                category="buah",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Bunga Kol",
                description="Bunga kol segar, kaya akan vitamin C",
                price=Decimal("11000.00"),
                stock=55,
                image="https://via.placeholder.com/300x300?text=Bunga+Kol",
                category="bunga",
                status="available",
                created_by=users[0].id
            ),
            Vegetables(
                name="Brokoli",
                description="Brokoli segar, baik untuk kesehatan tulang",
                price=Decimal("13000.00"),
                stock=65,
                image="https://via.placeholder.com/300x300?text=Brokoli",
                category="bunga",
                status="available",
                created_by=users[0].id
            )
        ]
        
        db.session.add_all(vegetables)
        db.session.commit()
        print(f"✓ {len(vegetables)} sayuran berhasil ditambahkan")
        
if __name__ == "__main__":
    seed()
