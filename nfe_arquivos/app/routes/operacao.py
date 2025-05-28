# routes/operacao.py
from flask import Blueprint, request, redirect, render_template
from app.models import db, NFeOperacao

bp = Blueprint('operacao', __name__, url_prefix='/operacao')

@bp.route('/receber', methods=['POST'])
def registrar_recebimento():
    op = NFeOperacao(
        chave=request.form.get('chave'),
        tipo='recebimento',
        responsavel=request.form.get('responsavel'),
        turno=request.form.get('turno'),
        quantidade=request.form.get('quantidade')
    )
    db.session.add(op)
    db.session.commit()
    return redirect('/operacao')

@bp.route('/expedir', methods=['POST'])
def registrar_expedicao():
    op = NFeOperacao(
        chave=request.form.get('chave'),
        tipo='expedicao',
        responsavel=request.form.get('responsavel'),
        destino=request.form.get('destino')
    )
    db.session.add(op)
    db.session.commit()
    return redirect('/operacao')