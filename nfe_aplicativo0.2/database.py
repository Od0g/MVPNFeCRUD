from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_login import UserMixin # Importar UserMixin
from werkzeug.security import generate_password_hash, check_password_hash # Para senhas seguras


db = SQLAlchemy()

# Modelo para o Cadastro de Usuários
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    matricula = db.Column(db.String(50), unique=True, nullable=False)
    funcao = db.Column(db.String(100))
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False) # Campo para a senha criptografada
    status = db.Column(db.String(20), default='Ativo')

    # Métodos para lidar com a senha
    def set_senha(self, senha): # Nome do método alterado para 'set_senha'
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha): # Nome do método alterado para 'check_senha'
        return check_password_hash(self.senha_hash, senha)

    # Relação com Recebimentos, Expedições e Protocolos
    recebimentos_feitos = db.relationship('Recebimento', backref='responsavel_recebimento_obj', lazy=True, foreign_keys='Recebimento.responsavel_recebimento_id')
    expedicoes_feitas = db.relationship('Expedicao', backref='responsavel_recebimento_exp_obj', lazy=True, foreign_keys='Expedicao.responsavel_recebimento_expedicao_id')
    protocolos_feitos = db.relationship('Protocolo', backref='responsavel_protocolo_obj', lazy=True, foreign_keys='Protocolo.responsavel_protocolo_id')

    def __repr__(self):
        return f'<Usuario {self.nome} ({self.matricula})>'

# (Seus outros modelos Recebimento, Expedicao, Protocolo aqui)
# Certifique-se de que os nomes dos campos correspondam ao seu app.py, por exemplo,
# em Expedicao: responsavel_recebimento_expedicao_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
# em Recebimento: responsavel_recebimento_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
# em Protocolo: responsavel_protocolo_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)


# Modelo para o Recebimento de NF-e
class Recebimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_recebimento = db.Column(db.DateTime, default=datetime.datetime.now) # Correção: datetime.datetime.now e não datetime.now
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
    data_expedicao = db.Column(db.DateTime, default=datetime.datetime.now) # Correção
    responsavel_entrega_expedicao = db.Column(db.String(255))
    responsavel_recebimento_expedicao_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    recebimento_id = db.Column(db.Integer, db.ForeignKey('recebimento.id'), unique=True, nullable=False) # Garante 1:1
    # status = db.Column(db.String(20), default='Concluido') # O status da expedição é inerentemente 'Concluído' em relação ao recebimento.
    turno = db.Column(db.String(50))


    responsavel_recebimento_expedicao = db.relationship('Usuario', backref='expedicoes_recebidas')
    recebimento_associado = db.relationship('Recebimento', backref=db.backref('expedicao', uselist=False)) # uselist=False para relação 1:1

    def __repr__(self):
        return f'<Expedicao para Recebimento ID: {self.recebimento_id}>'

# Modelo para o Protocolo
class Protocolo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_protocolo = db.Column(db.Date, default=datetime.date.today) # Correção
    periodo = db.Column(db.String(50), nullable=False) # 'Dia', 'Mês', 'Ano'
    total_notas_recebidas = db.Column(db.Integer, nullable=False)
    total_notas_expedidas = db.Column(db.Integer, nullable=False)
    responsavel_protocolo_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    observacoes = db.Column(db.Text)

    responsavel_protocolo = db.relationship('Usuario', backref='protocolos_gerados')

    def __repr__(self):
        return f'<Protocolo {self.data_protocolo} - {self.periodo}>'