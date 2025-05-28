# models.py
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='operacional')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class NFeArquivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(44), unique=True)
    fornecedor = db.Column(db.String(128))
    data_recebimento = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20))  # recebida ou expedida
    xml_path = db.Column(db.String(256))

class NFeOperacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(44))
    tipo = db.Column(db.String(20))  # recebimento ou expedicao
    responsavel = db.Column(db.String(128))
    turno = db.Column(db.String(20))
    quantidade = db.Column(db.Integer, nullable=True)
    destino = db.Column(db.String(128), nullable=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)

class NFe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(44), unique=True, nullable=False)
    fornecedor = db.Column(db.String(120), nullable=False)
    data_emissao = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='recebida')  # recebida | expedida
    xml_path = db.Column(db.String(255), nullable=False)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)