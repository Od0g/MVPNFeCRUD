from . import db
from datetime import datetime
from .extensions import db


class NFe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave_acesso = db.Column(db.String(44), unique=True, nullable=False)
    numero = db.Column(db.String(10), nullable=True)
    emitente_cnpj = db.Column(db.String(14), nullable=False)
    emitente_nome = db.Column(db.String(255), nullable=False)
    destinatario_cnpj = db.Column(db.String(14), nullable=False)
    destinatario_nome = db.Column(db.String(255), nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    data_emissao = db.Column(db.DateTime, nullable=False)
    xml_filename = db.Column(db.String(255), nullable=False)
    data_recebimento = db.Column(db.DateTime, default=datetime.utcnow) # Data de upload no sistema
    status = db.Column(db.String(50), default='Pendente') # Pendente, Recebida, Expedida, Devolvida

    # Campos de controle operacional
    responsavel_recebimento = db.Column(db.String(100), nullable=True)
    turno_recebimento = db.Column(db.String(50), nullable=True)
    quantidade_itens = db.Column(db.Integer, nullable=True)
    
    destino_expedicao = db.Column(db.String(255), nullable=True)
    responsavel_expedicao = db.Column(db.String(100), nullable=True)
    data_expedicao = db.Column(db.DateTime, nullable=True)
    email_responsavel_entrega = db.Column(db.String(255), nullable=True) # Para devoluções/expedição

    def __repr__(self):
        return f'<NFe {self.chave_acesso} - {self.emitente_nome}>'