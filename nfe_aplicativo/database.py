from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

# Modelo para o Cadastro de Usuários
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    matricula = db.Column(db.String(50), unique=True, nullable=False)
    funcao = db.Column(db.String(100))
    email = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Ativo')

    def __repr__(self):
        return f'<Usuario {self.nome}>'

# Modelo para o Recebimento de NF-e
class Recebimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_recebimento = db.Column(db.DateTime, default=datetime.datetime.now)
    responsavel_entrega = db.Column(db.String(255), nullable=False)
    responsavel_recebimento_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fornecedor = db.Column(db.String(255), nullable=False)
    chave_nfe = db.Column(db.String(44), unique=True, nullable=False)
    numero_nfe = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Pendente') # Pendente ou Concluído
    turno = db.Column(db.String(50))

    responsavel_recebimento = db.relationship('Usuario', backref='recebimentos_feitos')

    def __repr__(self):
        return f'<Recebimento {self.numero_nfe}>'

# Modelo para a Expedição de NF-e
class Expedicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_expedicao = db.Column(db.DateTime, default=datetime.datetime.now)
    responsavel_entrega_expedicao = db.Column(db.String(255))
    responsavel_recebimento_expedicao_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    recebimento_id = db.Column(db.Integer, db.ForeignKey('recebimento.id'), unique=True, nullable=False) # Garante 1:1
    status = db.Column(db.String(20), default='Concluido') # <<< Você pode querer adicionar isso aqui também
    turno = db.Column(db.String(50)) # <--- ADICIONE ESTA LINHA AQUI!


    responsavel_recebimento_expedicao = db.relationship('Usuario', backref='expedicoes_recebidas')
    recebimento_associado = db.relationship('Recebimento', backref='expedicao')

    def __repr__(self):
        return f'<Expedicao para Recebimento ID: {self.recebimento_id}>'

# Modelo para o Protocolo
class Protocolo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_protocolo = db.Column(db.Date, default=datetime.date.today)
    periodo = db.Column(db.String(50), nullable=False) # 'Dia', 'Mês', 'Ano'
    total_notas_recebidas = db.Column(db.Integer, nullable=False)
    total_notas_expedidas = db.Column(db.Integer, nullable=False)
    responsavel_protocolo_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    observacoes = db.Column(db.Text)

    responsavel_protocolo = db.relationship('Usuario', backref='protocolos_gerados')

    def __repr__(self):
        return f'<Protocolo {self.data_protocolo} - {self.periodo}>'