# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///gerenciador_nfe.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma_chave_secreta_muito_segura_para_flash_messages_PADRAO'
    # Adicionar outras configurações aqui, se necessário