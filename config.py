import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-default-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-default-jwt-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
