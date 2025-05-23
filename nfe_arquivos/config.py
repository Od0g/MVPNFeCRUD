import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'segredo-muito-seguro'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///nfe.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads/xml'
