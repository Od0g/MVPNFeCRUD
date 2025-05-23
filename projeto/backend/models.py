from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    matricula = db.Column(db.String(20), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    recebimentos = db.relationship('Recebimento', backref='usuario', lazy=True)
    expedicoes = db.relationship('Expedicao', backref='usuario', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Fornecedor(db.Model):
    __tablename__ = 'fornecedores'
    id = db.Column(db.Integer, primary_key=True)
    cnpj = db.Column(db.String(14), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    nfes = db.relationship('NFe', backref='fornecedor', lazy=True)

class NFe(db.Model):
    __tablename__ = 'nfes'
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(44), unique=True, nullable=False)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data_emissao = db.Column(db.DateTime, nullable=False)
    arquivo_path = db.Column(db.String(200), nullable=False)
    recebimentos = db.relationship('Recebimento', backref='nfe', lazy=True)
    expedicoes = db.relationship('Expedicao', backref='nfe', lazy=True)

class Recebimento(db.Model):
    __tablename__ = 'recebimentos'
    id = db.Column(db.Integer, primary_key=True)
    nfe_id = db.Column(db.Integer, db.ForeignKey('nfes.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_recebimento = db.Column(db.DateTime, default=datetime.now)
    turno = db.Column(db.String(20), nullable=False)

class Expedicao(db.Model):
    __tablename__ = 'expedicoes'
    id = db.Column(db.Integer, primary_key=True)
    nfe_id = db.Column(db.Integer, db.ForeignKey('nfes.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_expedicao = db.Column(db.DateTime, default=datetime.now)
    destino = db.Column(db.String(100), nullable=False)