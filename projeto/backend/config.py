import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SECRET_KEY = 'sua_chave_secreta_super_segura'

class Config:
    # Caminho absoluto para o banco de dados
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR}/database/nfe.db'  # Caminho corrigido
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Caminho absoluto para uploads
    UPLOAD_FOLDER = BASE_DIR / 'backend' / 'uploads'
    # Outras configurações
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'sua_chave_secreta_super_segura'
    TEMPLATES_FOLDER = BASE_DIR / 'frontend' / 'templates'