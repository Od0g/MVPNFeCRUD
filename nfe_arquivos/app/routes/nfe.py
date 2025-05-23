import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
from app import db
from app.models import NFe
from app.utils.xml_validator import extrair_dados_essenciais

bp = Blueprint('nfe', __name__, url_prefix='/nfe')

UPLOAD_FOLDER = 'uploads/xml'

@bp.route('/upload', methods=['POST'])
def upload_nfe():
    if 'xml' not in request.files:
        return jsonify({'message': 'Arquivo XML não enviado'}), 400
    
    file = request.files['xml']
    if file.filename == '':
        return jsonify({'message': 'Nome de arquivo vazio'}), 400

    dados = extrair_dados_essenciais(file)
    if not dados or not dados['chave']:
        return jsonify({'message': 'Erro ao validar XML'}), 400

    if NFe.query.filter_by(chave=dados['chave']).first():
        return jsonify({'message': 'NF-e já cadastrada'}), 400

    # Salvar arquivo com nome seguro
    file.seek(0)  # resetar ponteiro para salvar
    filename = secure_filename(f"{dados['chave']}.xml")
    caminho = os.path.join(UPLOAD_FOLDER, filename)
    file.save(caminho)

    # Persistir no banco
    nfe = NFe(
        chave=dados['chave'],
        fornecedor=dados['fornecedor'],
        data_emissao=datetime.fromisoformat(dados['data_emissao']),
        caminho_arquivo=caminho
    )
    db.session.add(nfe)
    db.session.commit()

    return jsonify({'message': 'NF-e cadastrada com sucesso'}), 201
