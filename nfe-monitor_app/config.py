import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default_secret_key_fallback' # Usado para sessões Flask
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), os.environ.get('STORAGE_PATH', 'storage'))
    ALLOWED_EXTENSIONS = {'xml'}