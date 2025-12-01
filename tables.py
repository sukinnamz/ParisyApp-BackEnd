from flask import Flask
from config import Config
from extensions import db
from models import Users, Vegetables, Transactions, DetailTransactions

def tables():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        db.drop_all()
        
        db.create_all()

if __name__ == "__main__":
    confirm = input("Reset table? (y/n): ")
    if confirm.lower() == 'y':
        tables()
    else:
        print("Reset database dibatalkan.")
