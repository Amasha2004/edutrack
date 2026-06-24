import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'edutrack-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///edutrack.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False