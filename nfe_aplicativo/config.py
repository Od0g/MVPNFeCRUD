# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///gerenciador_nfe.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Use variável de ambiente para a SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma_chave_secreta_muito_segura_para_desenvolvimento_PADRAO'

    # Adicionar outras configurações aqui, se necessário
    # Desative o modo de debug em produção
    DEBUG = False
    TESTING = False
    

