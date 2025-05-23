# backend/models.py
from . import db # AGORA importamos o 'db' do __init__.py (note o . para importação relativa)
from datetime import datetime

class NFeRecebida(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave_acesso = db.Column(db.String(44), unique=True, nullable=False)
    data_hora_recebimento = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    numero_nfe = db.Column(db.String(9), nullable=False)
    serie_nfe = db.Column(db.String(3), nullable=False)
    cnpj_fornecedor = db.Column(db.String(14), nullable=False)
    nome_fornecedor = db.Column(db.String(255), nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    usuario_recebimento = db.Column(db.String(100), nullable=False)
    regiao = db.Column(db.String(100))
    cliente_responsavel = db.Column(db.String(100))
    qualidade_observacao = db.Column(db.Text)
    caminho_xml = db.Column(db.String(255), nullable=False)
    validada = db.Column(db.Boolean, default=False)
    confirmacao_recebimento_fisico = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<NFeRecebida {self.chave_acesso}>'

class NFeExpedida(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave_acesso = db.Column(db.String(44), unique=True, nullable=False)
    data_hora_emissao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    numero_nfe = db.Column(db.String(9), nullable=False)
    serie_nfe = db.Column(db.String(3), nullable=False)
    cnpj_cliente = db.Column(db.String(14), nullable=False)
    nome_cliente = db.Column(db.String(255), nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    usuario_emissor = db.Column(db.String(100), nullable=False)
    regiao = db.Column(db.String(100))
    qualidade_observacao = db.Column(db.Text)
    caminho_xml = db.Column(db.String(255), nullable=False)
    status_sefaz = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<NFeExpedida {self.chave_acesso}>'