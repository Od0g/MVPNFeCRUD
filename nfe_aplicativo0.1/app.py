from flask import Flask, render_template, request, redirect, url_for, flash
from database import db, Usuario, Recebimento, Expedicao, Protocolo
import datetime
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased # Importe aliased aqui!
import requests # Para simular envio de e-mail

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gerenciador_nfe.db' # Nome do arquivo do banco de dados SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'uma_chave_secreta_muito_segura_para_flash_messages' # Chave para mensagens flash

db.init_app(app)

# Cria as tabelas do banco de dados se não existirem
with app.app_context():
    db.create_all()

# --- Rotas da Aplicação 
@app.route('/')
def index():
    return render_template('index.html')


## Aba: Cadastro

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        matricula = request.form['matricula']
        funcao = request.form['funcao']
        email = request.form['email']
        status = request.form['status']

        try:
            novo_usuario = Usuario(nome=nome, matricula=matricula, funcao=funcao, email=email, status=status)
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Usuário cadastrado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar usuário: {e}', 'danger')
        return redirect(url_for('cadastro'))
    usuarios = Usuario.query.all()
    return render_template('cadastro.html', usuarios=usuarios)

## Aba: Recebimento

@app.route('/recebimento', methods=['GET', 'POST'])
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
                status='Pendente', # Status inicial
                turno=turno
            )
            db.session.add(novo_recebimento)
            db.session.commit()

            # --- Simulação de Envio de E-mail             destinatarios = ['financeiro@empresa.com', 'compras@empresa.com'] # Exemplo de destinatários
            nfe_info = f"NF-e {numero_nfe} (Chave: {chave_nfe}) do fornecedor {fornecedor}"
            simular_envio_email(destinatarios, "Recebimento de NF-e", f"Uma nova NF-e foi recebida: {nfe_info}")
            flash('Recebimento registrado e e-mail simulado enviado com sucesso!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar recebimento: {e}', 'danger')
        return redirect(url_for('recebimento'))
    return render_template('recebimento.html', usuarios=usuarios)

## Aba: Expedição

@app.route('/expedicao', methods=['GET', 'POST'])
def expedicao():
    usuarios = Usuario.query.all()
    recebimentos_pendentes = Recebimento.query.filter_by(status='Pendente').all()

    if request.method == 'POST':
        recebimento_id = request.form['recebimento_id']
        responsavel_entrega_expedicao = request.form['responsavel_entrega_expedicao']
        responsavel_recebimento_expedicao_id = request.form['responsavel_recebimento_expedicao']
        turno = request.form['turno'] # Captura o turno do formulário

        try:
            # 1. Cria o registro de Expedição
            nova_expedicao = Expedicao(
                recebimento_id=recebimento_id,
                responsavel_entrega_expedicao=responsavel_entrega_expedicao,
                responsavel_recebimento_expedicao_id=responsavel_recebimento_expedicao_id,
                turno=turno # Adiciona o turno à expedição
            )
            db.session.add(nova_expedicao)

            # 2. Atualiza o status do Recebimento associado para 'Concluído'
            recebimento_associado = Recebimento.query.get(recebimento_id)
            if recebimento_associado:
                recebimento_associado.status = 'Concluído'

            db.session.commit()

            # --- Simulação de Envio de E-mail             destinatarios = ['logistica@empresa.com', 'cliente@empresa.com'] # Exemplo de destinatários
            nfe_info = f"NF-e {recebimento_associado.numero_nfe} (Chave: {recebimento_associado.chave_nfe}) foi expedida."
            simular_envio_email(destinatarios, "Expedição de NF-e", f"Uma NF-e foi expedida: {nfe_info}")
            flash('Expedição registrada e recebimento atualizado com sucesso!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar expedição: {e}', 'danger')
        return redirect(url_for('expedicao'))
    return render_template('expedicao.html', usuarios=usuarios, recebimentos_pendentes=recebimentos_pendentes)

## Aba: Relatório

@app.route('/relatorio')
def relatorio():
    # Alias para o segundo uso da tabela Usuario na expedição
    Usuario_exp = aliased(Usuario)

    # Consulta todos os recebimentos e, se houver, as expedições associadas
    # Usamos LEFT JOIN para incluir recebimentos que ainda não foram expedidos
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
        Expedicao.turno.label('turno_exp') # Agora 'turno' existe no modelo Expedicao
    ).outerjoin(Expedicao, Recebimento.id == Expedicao.recebimento_id)\
     .join(Usuario, Recebimento.responsavel_recebimento_id == Usuario.id)\
     .outerjoin(Usuario_exp, Expedicao.responsavel_recebimento_expedicao_id == Usuario_exp.id)\
     .all()

    # --- Dados para o Gráfico 1: Notas Recebidas vs. Expedidas por Mês     # Dicionário para armazenar contagens por mês {YYYY-MM: {'recebidas': X, 'expedidas': Y}}
    mensal_data = {}
    for recebimento in Recebimento.query.all():
        mes_ano = recebimento.data_recebimento.strftime('%Y-%m')
        if mes_ano not in mensal_data:
            mensal_data[mes_ano] = {'recebidas': 0, 'expedidas': 0}
        mensal_data[mes_ano]['recebidas'] += 1

    for expedicao in Expedicao.query.all():
        mes_ano = expedicao.data_expedicao.strftime('%Y-%m')
        if mes_ano not in mensal_data:
            mensal_data[mes_ano] = {'recebidas': 0, 'expedidas': 0} # Garante que o mês exista mesmo se só tiver expedição
        mensal_data[mes_ano]['expedidas'] += 1

    # Ordenar os meses cronologicamente
    # Converte chaves para objetos datetime para ordenação correta e depois formata de volta
    meses_ordenados_dt = sorted(mensal_data.keys(), key=lambda x: datetime.datetime.strptime(x, '%Y-%m'))
    labels_meses = [datetime.datetime.strptime(m, '%Y-%m').strftime('%b/%Y') for m in meses_ordenados_dt] # Jan/2025
    data_recebidas_mensal = [mensal_data[m]['recebidas'] for m in meses_ordenados_dt]
    data_expedidas_mensal = [mensal_data[m]['expedidas'] for m in meses_ordenados_dt]


    # --- Dados para o Gráfico 2: Status das Notas (Pendentes vs. Concluídas)     total_pendentes = Recebimento.query.filter_by(status='Pendente').count()
    total_pendentes = Recebimento.query.filter_by(status='Pendente').count()
    total_concluidas = Recebimento.query.filter_by(status='Concluído').count()



    # Passar os dados para o template
    return render_template('relatorio.html',
                           dados_relatorio=dados_relatorio,
                           labels_meses=labels_meses,
                           data_recebidas_mensal=data_recebidas_mensal,
                           data_expedidas_mensal=data_expedidas_mensal,
                           total_pendentes=total_pendentes,
                           total_concluidas=total_concluidas)

## Aba: Protocolo

@app.route('/protocolo', methods=['GET', 'POST'])
def protocolo():
    usuarios = Usuario.query.all()
    protocolos_registrados = Protocolo.query.order_by(Protocolo.data_protocolo.desc()).all()

    if request.method == 'POST':
        data_protocolo_str = request.form['data_protocolo']
        periodo = request.form['periodo']
        responsavel_protocolo_id = request.form['responsavel_protocolo']
        observacoes = request.form['observacoes']

        data_protocolo = datetime.datetime.strptime(data_protocolo_str, '%Y-%m-%d').date()

        # Contagem de notas para o período selecionado
        if periodo == 'Dia':
            total_recebidas = Recebimento.query.filter(
                func.date(Recebimento.data_recebimento) == data_protocolo
            ).count()
            total_expedidas = db.session.query(Expedicao).join(Recebimento).filter(
                func.date(Recebimento.data_expedicao) == data_protocolo # Corrigido para data_expedicao
            ).count()
        elif periodo == 'Mês':
            total_recebidas = Recebimento.query.filter(
                func.strftime('%Y-%m', Recebimento.data_recebimento) == data_protocolo.strftime('%Y-%m')
            ).count()
            total_expedidas = db.session.query(Expedicao).join(Recebimento).filter(
                func.strftime('%Y-%m', Expedicao.data_expedicao) == data_protocolo.strftime('%Y-%m') # Corrigido para data_expedicao
            ).count()
        elif periodo == 'Ano':
            total_recebidas = Recebimento.query.filter(
                func.strftime('%Y', Recebimento.data_recebimento) == data_protocolo.strftime('%Y')
            ).count()
            total_expedidas = db.session.query(Expedicao).join(Recebimento).filter(
                func.strftime('%Y', Expedicao.data_expedicao) == data_protocolo.strftime('%Y') # Corrigido para data_expedicao
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
        return redirect(url_for('protocolo'))
    return render_template('protocolo.html', usuarios=usuarios, protocolos_registrados=protocolos_registrados)

# --- Simulação de Envio de E-mail (Função Auxiliar) def simular_envio_email(destinatarios, assunto, corpo):
    print(f"\n--- SIMULAÇÃO DE ENVIO DE E-MAIL ---")
    print(f"Para: {', '.join(destinatarios)}")
    print(f"Assunto: {assunto}")
    print(f"Corpo:\n{corpo}")
    print(f"-----------------------------------\n")
    # Em uma aplicação real, aqui você usaria smtplib ou uma API de e-mail.
    # requests.post('https://api.emailservice.com/send', json={'to': destinatarios, 'subject': assunto, 'body': corpo})

if __name__ == '__main__':
    app.run(debug=True)