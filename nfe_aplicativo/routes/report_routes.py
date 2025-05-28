# routes/report_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db, Usuario, Recebimento, Expedicao, Protocolo
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased
import datetime

report = Blueprint('report', __name__)

# --- Rotas de Relatório ---
@report.route('/relatorio')
@login_required # Somente usuários logados podem acessar
def relatorio():
    Usuario_exp = aliased(Usuario)

    dados_relatorio = db.session.query(
        Recebimento.data_recebimento,
        Recebimento.fornecedor,
        Recebimento.numero_nfe,
        Recebimento.chave_nfe,
        Recebimento.responsavel_entrega.label('resp_entrega_rec'),
        Usuario.nome.label('resp_recebimento_nome'),
        Usuario.matricula.label('resp_recebimento_matricula'),
        Recebimento.turno.label('turno_rec'),
        Recebimento.status,
        Expedicao.data_expedicao,
        Expedicao.id.label('expedicao_id'),
        Usuario_exp.nome.label('resp_recebimento_exp_nome'),
        Usuario_exp.matricula.label('resp_recebimento_exp_matricula'),
        Expedicao.turno.label('turno_exp')
    ).outerjoin(Expedicao, Recebimento.id == Expedicao.recebimento_id)\
     .join(Usuario, Recebimento.responsavel_recebimento_id == Usuario.id)\
     .outerjoin(Usuario_exp, Expedicao.responsavel_recebimento_expedicao_id == Usuario_exp.id)\
     .all()

    # --- Dados para o Gráfico 1: Notas Recebidas vs. Expedidas por Mês ---
    mensal_data = {}
    for recebimento in Recebimento.query.all():
        mes_ano = recebimento.data_recebimento.strftime('%Y-%m')
        if mes_ano not in mensal_data:
            mensal_data[mes_ano] = {'recebidas': 0, 'expedidas': 0}
        mensal_data[mes_ano]['recebidas'] += 1

    for expedicao in Expedicao.query.all():
        mes_ano = expedicao.data_expedicao.strftime('%Y-%m')
        if mes_ano not in mensal_data:
            mensal_data[mes_ano] = {'recebidas': 0, 'expedidas': 0}
        mensal_data[mes_ano]['expedidas'] += 1

    meses_ordenados_dt = sorted(mensal_data.keys(), key=lambda x: datetime.datetime.strptime(x, '%Y-%m'))
    labels_meses = [datetime.datetime.strptime(m, '%Y-%m').strftime('%b/%Y') for m in meses_ordenados_dt]
    data_recebidas_mensal = [mensal_data[m]['recebidas'] for m in meses_ordenados_dt]
    data_expedidas_mensal = [mensal_data[m]['expedidas'] for m in meses_ordenados_dt]

    # --- Dados para o Gráfico 2: Status das Notas (Pendentes vs. Concluídas) ---
    total_pendentes = Recebimento.query.filter_by(status='Pendente').count()
    total_concluidas = Recebimento.query.filter_by(status='Concluído').count()

    return render_template('relatorio.html',
                           dados_relatorio=dados_relatorio,
                           labels_meses=labels_meses,
                           data_recebidas_mensal=data_recebidas_mensal,
                           data_expedidas_mensal=data_expedidas_mensal,
                           total_pendentes=total_pendentes,
                           total_concluidas=total_concluidas)

# --- Rotas de Protocolo ---
@report.route('/protocolo', methods=['GET', 'POST'])
@login_required # Somente usuários logados podem acessar
def protocolo():
    usuarios = Usuario.query.all()
    protocolos_registrados = Protocolo.query.order_by(Protocolo.data_protocolo.desc()).all()

    if request.method == 'POST':
        data_protocolo_str = request.form['data_protocolo']
        periodo = request.form['periodo']
        responsavel_protocolo_id = request.form['responsavel_protocolo']
        observacoes = request.form['observacoes']

        data_protocolo = datetime.datetime.strptime(data_protocolo_str, '%Y-%m-%d').date()

        if periodo == 'Dia':
            total_recebidas = Recebimento.query.filter(
                func.date(Recebimento.data_recebimento) == data_protocolo
            ).count()
            total_expedidas = db.session.query(Expedicao).join(Recebimento).filter(
                func.date(Expedicao.data_expedicao) == data_protocolo
            ).count()
        elif periodo == 'Mês':
            total_recebidas = Recebimento.query.filter(
                func.strftime('%Y-%m', Recebimento.data_recebimento) == data_protocolo.strftime('%Y-%m')
            ).count()
            total_expedidas = db.session.query(Expedicao).join(Recebimento).filter(
                func.strftime('%Y-%m', Expedicao.data_expedicao) == data_protocolo.strftime('%Y-%m')
            ).count()
        elif periodo == 'Ano':
            total_recebidas = Recebimento.query.filter(
                func.strftime('%Y', Recebimento.data_recebimento) == data_protocolo.strftime('%Y')
            ).count()
            total_expedidas = db.session.query(Expedicao).join(Recebimento).filter(
                func.strftime('%Y', Expedicao.data_expedicao) == data_protocolo.strftime('%Y')
            ).count()
        else:
            total_recebidas = 0
            total_expedidas = 0

        try:
            novo_protocolo = Protocolo(
                data_protocolo=data_protocolo,
                periodo=periodo,
                total_notas_recebidas=total_recebidas,
                total_notas_expedidas=total_expedidas,
                responsavel_protocolo_id=responsavel_protocolo_id,
                observacoes=observacoes
            )
            db.session.add(novo_protocolo)
            db.session.commit()
            flash('Protocolo registrado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar protocolo: {e}', 'danger')
        return redirect(url_for('report.protocolo'))
    return render_template('protocolo.html', usuarios=usuarios, protocolos_registrados=protocolos_registrados)