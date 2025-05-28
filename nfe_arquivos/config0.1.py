import os

class Config:
    SECRET_KEY = '101203'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///nfe.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'troque_essa_chave_jwt'

    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads/xml')

    # Config SMTP para envio de e-mails
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'admin'     # <== configure aqui
    MAIL_PASSWORD = 'admin123'           # <== configure aqui
    MAIL_USE_TLS = True
