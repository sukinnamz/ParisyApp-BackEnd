import os
from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///market.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "supersecretkey"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    SECRET_KEY = "supersecretkey"
    SESSION_TYPE = "filesystem"
