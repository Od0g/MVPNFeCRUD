import os
from flask import Blueprint, request, redirect, url_for, current_app, flash
from werkzeug.utils import secure_filename
from datetime import datetime
from app import db
from app.models import NFe
from app.utils.xml_validator import extrair_dados_essenciais

bp = Blueprint('nfe', __name__, url_prefix='/nfe')

@bp.route('/upload', methods=['POST'])
def upload_nfe():
    # Verifica se o arquivo XML foi enviado.
    if 'xml' not in request.files:
        flash('Arquivo XML não enviado', 'error')
        return redirect(url_for('index'))
    
    file = request.files['xml']
    if file.filename == '':
        flash('Nome de arquivo vazio', 'error')
        return redirect(url_for('index'))

    # Extrai dados essenciais do XML.
    dados = extrair_dados_essenciais(file)
    if not dados or not dados.get('chave'):
        flash('Erro ao validar XML', 'error')
        return redirect(url_for('index'))

    # Verifica se a NF-e já está cadastrada.
    if NFe.query.filter_by(chave=dados['chave']).first():
        flash('NF-e já cadastrada', 'info')
        return redirect(url_for('index'))

    # Salva o arquivo no diretório definido.
    file.seek(0)
    filename = secure_filename(f"{dados['chave']}.xml")
    caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(caminho)

    # Cria o registro da NF-e no banco de dados.
    nfe = NFe(
        chave=dados['chave'],
        fornecedor=dados['fornecedor'],
        data_emissao=datetime.fromisoformat(dados['data_emissao']),
        xml_path=caminho  # Nome do atributo conforme definido no modelo
    )
    db.session.add(nfe)
    db.session.commit()

    flash('NF-e cadastrada com sucesso!', 'success')
    return redirect(url_for('index'))
