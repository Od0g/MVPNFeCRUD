# app.py Beta 0.2.3
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nfe.db'
app.config['UPLOAD_FOLDER'] = 'nfe_arquivos'
db = SQLAlchemy(app)

class Fornecedor(db.Model):
    __tablename__ = 'fornecedor'
    id = db.Column(db.Integer, primary_key=True)
    cnpj = db.Column(db.String(14), unique=True)
    nome = db.Column(db.String(100))

class NFe(db.Model):
    __tablename__ = 'nfe'
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(44), unique=True)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedor.id'))
    quantidade = db.Column(db.Integer)
    data_hora = db.Column(db.DateTime, default=datetime.now)
    arquivo_path = db.Column(db.String(200))
    fornecedor = db.relationship('Fornecedor', backref='nfes')

class Recebimento(db.Model):
    __tablename__ = 'recebimento'
    id = db.Column(db.Integer, primary_key=True)
    nfe_id = db.Column(db.Integer, db.ForeignKey('nfe.id'))
    matricula_responsavel = db.Column(db.String(20))
    turno = db.Column(db.String(20))
    data = db.Column(db.DateTime, default=datetime.now)
    nfe = db.relationship('NFe', backref='recebimento')

class Expedicao(db.Model):
    __tablename__ = 'expedicao'
    id = db.Column(db.Integer, primary_key=True)
    nfe_id = db.Column(db.Integer, db.ForeignKey('nfe.id'))
    matricula_responsavel = db.Column(db.String(20))
    destino = db.Column(db.String(100))
    data = db.Column(db.DateTime, default=datetime.now)
    nfe = db.relationship('NFe', backref='expedicao')

@app.route('/processar-xml', methods=['POST'])
def processar_xml():
    try:
        file = request.files['xml']
        tree = ET.parse(file.stream)
        root = tree.getroot()
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        chave = root.find('.//nfe:infNFe', ns).attrib['Id'][3:]
        cnpj_emitente = root.find('.//nfe:emit/nfe:CNPJ', ns).text
        nome_emitente = root.find('.//nfe:emit/nfe:xNome', ns).text
        quantidade = len(root.findall('.//nfe:det', ns))
        
        return jsonify({
            'success': True,
            'data': {
                'chave': chave,
                'cnpj': cnpj_emitente,
                'fornecedor': nome_emitente,
                'quantidade': quantidade
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/')
def index():
    return render_template('index.html')

# Novas rotas para operações
@app.route('/receber', methods=['POST'])
def receber_nfe():
    data = request.form
    try:
        # Cadastrar fornecedor se não existir
        fornecedor = Fornecedor.query.filter_by(cnpj=data['cnpj']).first()
        if not fornecedor:
            fornecedor = Fornecedor(cnpj=data['cnpj'], nome=data['fornecedor'])
            db.session.add(fornecedor)
            db.session.commit()

        # Processar NFe
        nfe = NFe(
            chave=data['chave'],
            fornecedor_id=fornecedor.id,
            quantidade=data['quantidade'],
            data_hora=datetime.now()
        )
        db.session.add(nfe)
        db.session.commit()

        # Registrar recebimento
        recebimento = Recebimento(
            nfe_id=nfe.id,
            responsavel_entrega=data['responsavel_entrega'],
            matricula_recebimento=data['matricula_recebimento'],
            turno=data['turno']
        )
        db.session.add(recebimento)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/expedir', methods=['POST'])
def expedir_nfe():
    data = request.form
    try:
        # Similar ao recebimento
        fornecedor = Fornecedor.query.filter_by(cnpj=data['cnpj']).first()
        if not fornecedor:
            fornecedor = Fornecedor(cnpj=data['cnpj'], nome=data['fornecedor'])
            db.session.add(fornecedor)
            db.session.commit()

        nfe = NFe(
            chave=data['chave'],
            fornecedor_id=fornecedor.id,
            quantidade=data['quantidade'],
            data_hora=datetime.now()
        )
        db.session.add(nfe)
        db.session.commit()

        expedicao = Expedicao(
            nfe_id=nfe.id,
            responsavel_expedicao=data['responsavel_expedicao'],
            matricula_expedicao=data['matricula_expedicao'],
            destino=data['destino']
        )
        db.session.add(expedicao)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/relatorio')
def relatorio():
    recebimentos = db.session.query(
        Recebimento,
        NFe,
        Fornecedor
    ).join(
        NFe, Recebimento.nfe_id == NFe.id
    ).join(
        Fornecedor, NFe.fornecedor_id == Fornecedor.id
    ).all()
    
    expedicoes = db.session.query(
        Expedicao,
        NFe,
        Fornecedor
    ).join(
        NFe, Expedicao.nfe_id == NFe.id
    ).join(
        Fornecedor, NFe.fornecedor_id == Fornecedor.id
    ).all()
    
    return render_template('relatorio.html', 
        recebimentos=recebimentos,
        expedicoes=expedicoes)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

@app.route('/enviar-email/<tipo>/<int:id>')
def enviar_email(tipo, id):
    # Implementação básica de envio de email
    # (Substituir por lógica real de envio)
    return jsonify({'status': 'Email enviado'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)