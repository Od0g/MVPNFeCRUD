from . import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='operacional')  # admin ou operacional

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
from datetime import datetime

class NFe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(44), unique=True, nullable=False)
    fornecedor = db.Column(db.String(120), nullable=False)
    data_emissao = db.Column(db.DateTime, nullable=False)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='recebida')  # recebida/expedida
    caminho_arquivo = db.Column(db.String(200), nullable=False)

class Operacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # 'recebimento' ou 'expedicao'
    responsavel = db.Column(db.String(100), nullable=False)
    turno = db.Column(db.String(20), nullable=False)
    destino = db.Column(db.String(120), nullable=False)
    qtd_itens = db.Column(db.Integer, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    nfe_id = db.Column(db.Integer, db.ForeignKey('n_fe.id'), nullable=False)
    nfe = db.relationship('NFe', backref='operacoes')