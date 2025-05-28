# routes/nfe_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db, Usuario, Recebimento, Expedicao
import requests # Para simular envio de e-mail

nfe = Blueprint('nfe', __name__)

# --- Funções auxiliares (pode ser movida para um 'utils.py' se crescer) ---
def simular_envio_email(destinatarios, assunto, corpo):
    print(f"\n--- SIMULAÇÃO DE ENVIO DE E-MAIL ---")
    print(f"Para: {', '.join(destinatarios)}")
    print(f"Assunto: {assundo}")
    print(f"Corpo:\n{corpo}")
    print(f"-----------------------------------\n")

# --- Rotas de Recebimento ---
@nfe.route('/recebimento', methods=['GET', 'POST'])
@login_required # Somente usuários logados podem acessar
def recebimento():
    usuarios = Usuario.query.all()
    if request.method == 'POST':
        responsavel_entrega = request.form['responsavel_entrega']
        responsavel_recebimento_id = request.form['responsavel_recebimento']
        fornecedor = request.form['fornecedor']
        chave_nfe = request.form['chave_nfe']
        numero_nfe = request.form['numero_nfe']
        turno = request.form['turno']

        try:
            novo_recebimento = Recebimento(
                responsavel_entrega=responsavel_entrega,
                responsavel_recebimento_id=responsavel_recebimento_id,
                fornecedor=fornecedor,
                chave_nfe=chave_nfe,
                numero_nfe=numero_nfe,
                status='Pendente',
                turno=turno
            )
            db.session.add(novo_recebimento)
            db.session.commit()

            destinatarios = ['financeiro@empresa.com', 'compras@empresa.com']
            nfe_info = f"NF-e {numero_nfe} (Chave: {chave_nfe}) do fornecedor {fornecedor}"
            simular_envio_email(destinatarios, "Recebimento de NF-e", f"Uma nova NF-e foi recebida: {nfe_info}")
            flash('Recebimento registrado e e-mail simulado enviado com sucesso!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar recebimento: {e}', 'danger')
        return redirect(url_for('nfe.recebimento'))
    return render_template('recebimento.html', usuarios=usuarios)

# --- Rotas de Expedição ---
@nfe.route('/expedicao', methods=['GET', 'POST'])
@login_required # Somente usuários logados podem acessar
def expedicao():
    usuarios = Usuario.query.all()
    recebimentos_pendentes = Recebimento.query.filter_by(status='Pendente').all()

    if request.method == 'POST':
        recebimento_id = request.form['recebimento_id']
        responsavel_entrega_expedicao = request.form['responsavel_entrega_expedicao']
        responsavel_recebimento_expedicao_id = request.form['responsavel_recebimento_expedicao']
        turno = request.form['turno']

        try:
            nova_expedicao = Expedicao(
                recebimento_id=recebimento_id,
                responsavel_entrega_expedicao=responsavel_entrega_expedicao,
                responsavel_recebimento_expedicao_id=responsavel_recebimento_expedicao_id,
                turno=turno
            )
            db.session.add(nova_expedicao)

            recebimento_associado = Recebimento.query.get(recebimento_id)
            if recebimento_associado:
                recebimento_associado.status = 'Concluído'

            db.session.commit()

            destinatarios = ['logistica@empresa.com', 'cliente@empresa.com']
            nfe_info = f"NF-e {recebimento_associado.numero_nfe} (Chave: {recebimento_associado.chave_nfe}) foi expedida."
            simular_envio_email(destinatarios, "Expedição de NF-e", f"Uma NF-e foi expedida: {nfe_info}")
            flash('Expedição registrada e recebimento atualizado com sucesso!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar expedição: {e}', 'danger')
        return redirect(url_for('nfe.expedicao'))
    return render_template('expedicao.html', usuarios=usuarios, recebimentos_pendentes=recebimentos_pendentes)