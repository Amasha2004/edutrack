import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'edutrack-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///edutrack.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your-gmail@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your-app-password'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME') or 'your-gmail@gmail.com'