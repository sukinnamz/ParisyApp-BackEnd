import os

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///market.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "supersecretkey"
