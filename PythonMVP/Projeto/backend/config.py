import os

class Config:
    # Chave secreta para segurança da sessão (importante para Flask)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma_chave_muito_secreta_e_dificil'
    # Configuração do banco de dados SQLite
    # O caminho para o arquivo do DB, relativo à raiz do projeto
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'nfe.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Desativa o rastreamento de modificações para otimização