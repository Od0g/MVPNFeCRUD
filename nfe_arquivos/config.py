import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///nfe.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret')

    UPLOAD_FOLDER = os.path.join(os.getcwd(), '/workspaces/MVPNFeCRUD/nfe_arquivos/uploads')

    # Configuração SMTP para envio de e-mails
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'admin')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'admin123')
    MAIL_USE_TLS = True
