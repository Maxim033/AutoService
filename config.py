import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # правильный путь к базе SQLite
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'autoservice.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")
