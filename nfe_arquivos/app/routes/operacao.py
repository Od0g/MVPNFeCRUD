from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import NFe
from app.utils.email_sender import enviar_email  # você vai criar isso
from flask import Blueprint, request, jsonify, render_template






bp = Blueprint('operacao', __name__, url_prefix='/operacao')

@bp.route('/')
def operacao_page():
    return render_template('operacao.html')


@bp.route('/registrar', methods=['POST'])
def registrar_operacao():
    data = request.json
    chave = data.get('chave')
    tipo = data.get('tipo')  # 'recebida' ou 'expedida'

    if tipo not in ['recebida', 'expedida']:
        return jsonify({'message': 'Tipo de operação inválido'}), 400

    nfe = NFe.query.filter_by(chave=chave).first()
    if not nfe:
        return jsonify({'message': 'NF-e não encontrada'}), 404

    nfe.status = tipo
    db.session.commit()

    # Enviar e-mail com dados da NF-e
    enviar_email(
        assunto=f'NF-e {tipo.upper()} registrada',
        destinatario='destinatario@empresa.com',
        corpo=f"NF-e {nfe.chave} ({nfe.fornecedor}) foi marcada como '{nfe.status}' em {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}"
    )

    return jsonify({'message': f'Operação "{tipo}" registrada com sucesso'}), 200
