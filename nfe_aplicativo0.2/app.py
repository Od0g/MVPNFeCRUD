from flask import Flask, render_template, request, redirect, url_for, flash, session, current_app
from database import db, Usuario, Recebimento, Expedicao, Protocolo
import datetime
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased
import requests # Para simular envio de e-mail
from functools import wraps # Para criar o decorator de login

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gerenciador_nfe.db' # Nome do arquivo do banco de dados SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'uma_chave_secreta_muito_segura_para_flash_messages' # Chave para mensagens flash

db.init_app(app)

# Cria as tabelas do banco de dados se não existirem
with app.app_context():
    db.create_all()



# Decorator para exigir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Context Processor para disponibilizar variáveis globais nos templates ---
# Este é o ponto crucial para o erro que você está vendo.
@app.context_processor
def inject_global_data():
    # 'logged_in' será True se 'usuario_id' estiver na sessão
    logged_in = 'usuario_id' in session
    # 'current_user_name' será o nome do usuário ou None se não logado
    current_user_name = session.get('usuario_nome')
    
    return {
        'current_year': datetime.datetime.now().year,
        'logged_in': logged_in,
        'current_user_name': current_user_name
    }

# --- Rotas da Aplicação ---

@app.route('/')
def index():
    # Não precisa mais passar current_year e current_user aqui, pois são injetados globalmente.
    return render_template('index.html')

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Se o usuário já está logado, redireciona para a página inicial
    if 'usuario_id' in session:
        flash(f'Você já está logado como {session["usuario_nome"]}.', 'info')
        return redirect(url_for('index'))

    if request.method == 'POST':
        matricula = request.form['matricula']
        senha = request.form['senha'] # Você está usando 'senha' no formulário e no modelo

        usuario = Usuario.query.filter_by(matricula=matricula).first()

        # Certifique-se de que o método no seu modelo Usuario é 'check_senha' (e não 'check_password')
        if usuario and usuario.check_senha(senha):
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome # Armazena o nome na sessão
            flash(f'Login bem-sucedido, {usuario.nome}!', 'success')
            return redirect(url_for('index')) # Redireciona para a página inicial após o login
        else:
            flash('Matrícula ou senha inválidos.', 'danger')
    return render_template('login.html') # current_year é injetado globalmente

# Rota de Logout
@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('usuario_nome', None) # Remove o nome também
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login')) # Redireciona para a página de login após o logout

## Aba: Cadastro (Ajustada para incluir senha e ser protegida)
@app.route('/cadastro', methods=['GET', 'POST'])
@login_required # Apenas usuários logados podem cadastrar novos usuários
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        matricula = request.form['matricula']
        funcao = request.form['funcao']
        email = request.form['email']
        password_from_form = request.form['senha'] # Usar um nome de variável diferente para evitar conflito

        # Verifica se a senha está vazia
        if not password_from_form:
            flash('O campo senha é obrigatório.', 'danger')
            # Retorne o template para mostrar a mensagem sem tentar cadastrar
            usuarios = Usuario.query.all()
            return render_template('cadastro.html', usuarios=usuarios)

        status = request.form['status']

        # Verificar se matrícula ou email já existem
        existing_user_matricula = Usuario.query.filter_by(matricula=matricula).first()
        existing_user_email = Usuario.query.filter_by(email=email).first()

        if existing_user_matricula:
            flash('Matrícula já cadastrada.', 'danger')
        elif existing_user_email:
            flash('E-mail já cadastrado.', 'danger')
        else:
            try:
                novo_usuario = Usuario(nome=nome, matricula=matricula, funcao=funcao, email=email, status=status)
                # Certifique-se de que o método no seu modelo Usuario é 'set_senha' (e não 'set_password')
                novo_usuario.set_senha(password_from_form) # Armazena o hash da senha
                db.session.add(novo_usuario)
                db.session.commit()
                flash('Usuário cadastrado com sucesso!', 'success')
                return redirect(url_for('cadastro'))
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao cadastrar usuário: {e}', 'danger')
    
    usuarios = Usuario.query.all()
    return render_template('cadastro.html', usuarios=usuarios)


## Aba: Recebimento
@app.route('/recebimento', methods=['GET', 'POST'])
@login_required # Protege a rota
def recebimento():
    usuarios_ativos = Usuario.query.filter_by(status='Ativo').all() # Filtrar apenas usuários ativos
    if request.method == 'POST':
        responsavel_entrega = request.form['responsavel_entrega']
        responsavel_recebimento_id = request.form['responsavel_recebimento']
        fornecedor = request.form['fornecedor']
        chave_nfe = request.form['chave_nfe']
        numero_nfe = request.form['numero_nfe']
        turno = request.form['turno']

        # Validação do responsável pelo recebimento
        responsavel_obj = Usuario.query.get(responsavel_recebimento_id)
        if not responsavel_obj or responsavel_obj.status != 'Ativo':
            flash('Responsável pelo recebimento inválido ou inativo.', 'danger')
            return redirect(url_for('recebimento'))

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

            # --- Simulação de Envio de E-mail ---
            destinatarios = ['financeiro@empresa.com', 'augusto_inacio@lslgr.com.br', 'compras@empresa.com'] # Exemplo de destinatários
            nfe_info = f"NF-e {numero_nfe} (Chave: {chave_nfe}) do fornecedor {fornecedor}"
            # Usa o nome do responsável pela recepção
            simular_envio_email(destinatarios, "Recebimento de NF-e", f"Uma nova NF-e foi recebida: {nfe_info} por {responsavel_obj.nome}.")
            flash('Recebimento registrado e e-mail simulado enviado com sucesso!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar recebimento: {e}', 'danger')
        return redirect(url_for('recebimento'))
    return render_template('recebimento.html', usuarios=usuarios_ativos)


## Aba: Expedição
@app.route('/expedicao', methods=['GET', 'POST'])
@login_required # Protege a rota
def expedicao():
    usuarios_ativos = Usuario.query.filter_by(status='Ativo').all()
    recebimentos_pendentes = Recebimento.query.filter_by(status='Pendente').all()

    if request.method == 'POST':
        recebimento_id = request.form['recebimento_id']
        responsavel_entrega_expedicao = request.form['responsavel_entrega_expedicao']
        responsavel_recebimento_expedicao_id = request.form['responsavel_recebimento_expedicao']
        turno = request.form['turno']

        # Validação do responsável pela expedição
        responsavel_obj = Usuario.query.get(responsavel_recebimento_expedicao_id)
        if not responsavel_obj or responsavel_obj.status != 'Ativo':
            flash('Responsável pela expedição inválido ou inativo.', 'danger')
            return redirect(url_for('expedicao'))

        recebimento_associado = Recebimento.query.get(recebimento_id)
        if not recebimento_associado:
            flash('Recebimento não encontrado.', 'danger')
            return redirect(url_for('expedicao'))
        if recebimento_associado.status == 'Concluído':
            flash('Este recebimento já foi expedido.', 'warning')
            return redirect(url_for('expedicao'))


        try:
            # 1. Cria o registro de Expedição
            nova_expedicao = Expedicao(
                recebimento_id=recebimento_id,
                responsavel_entrega_expedicao=responsavel_entrega_expedicao,
                responsavel_recebimento_expedicao_id=responsavel_recebimento_expedicao_id,
                turno=turno
            )
            db.session.add(nova_expedicao)

            # 2. Atualiza o status do Recebimento associado para 'Concluído'
            recebimento_associado.status = 'Concluído'

            db.session.commit()

            # --- Simulação de Envio de E-mail ---
            destinatarios = ['logistica@empresa.com', 'cliente@empresa.com'] # Exemplo de destinatários
            nfe_info = f"NF-e {recebimento_associado.numero_nfe} (Chave: {recebimento_associado.chave_nfe}) foi expedida."
            # Usa o nome do responsável pela expedição
            simular_envio_email(destinatarios, "Expedição de NF-e", f"Uma NF-e foi expedida: {nfe_info} por {responsavel_obj.nome}.")
            flash('Expedição registrada e recebimento atualizado com sucesso!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar expedição: {e}', 'danger')
        return redirect(url_for('expedicao'))
    return render_template('expedicao.html', usuarios=usuarios_ativos, recebimentos_pendentes=recebimentos_pendentes)


## Aba: Relatório
@app.route('/relatorio')
@login_required # Protege a rota
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
    # Dicionário para armazenar contagens por mês {YYYY-MM: {'recebidas': X, 'expedidas': Y}}
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
    meses_ordenados = sorted(mensal_data.keys())
    labels_meses = [datetime.datetime.strptime(m, '%Y-%m').strftime('%b/%Y') for m in meses_ordenados] # Jan/2025
    data_recebidas_mensal = [mensal_data[m]['recebidas'] for m in meses_ordenados]
    data_expedidas_mensal = [mensal_data[m]['expedidas'] for m in meses_ordenados]

    # --- Dados para o Gráfico 2: Status das Notas (Pendentes vs. Concluídas) ---
    total_pendentes = Recebimento.query.filter_by(status='Pendente').count()
    total_concluidas = Recebimento.query.filter_by(status='Concluído').count()

    # Passar os dados para o template
    return render_template('relatorio.html',
                            dados_relatorio=dados_relatorio,
                            labels_meses=labels_meses,
                            data_recebidas_mensal=data_recebidas_mensal,
                            data_expedidas_mensal=data_expedidas_mensal,
                            total_pendentes=total_pendentes,
                            total_concluidas=total_concluidas) # current_year é injetado globalmente


## Aba: Protocolo
@app.route('/protocolo', methods=['GET', 'POST'])
@login_required # Protege a rota
def protocolo():
    usuarios_ativos = Usuario.query.filter_by(status='Ativo').all() # Filtrar apenas usuários ativos
    protocolos_registrados = Protocolo.query.order_by(Protocolo.data_protocolo.desc()).all()

    if request.method == 'POST':
        data_protocolo_str = request.form['data_protocolo']
        periodo = request.form['periodo']
        responsavel_protocolo_id = request.form['responsavel_protocolo']
        observacoes = request.form['observacoes']

        # Validação do responsável pelo protocolo
        responsavel_obj = Usuario.query.get(responsavel_protocolo_id)
        if not responsavel_obj or responsavel_obj.status != 'Ativo':
            flash('Responsável pelo protocolo inválido ou inativo.', 'danger')
            return redirect(url_for('protocolo'))


        data_protocolo = datetime.datetime.strptime(data_protocolo_str, '%Y-%m-%d').date()

        # Contagem de notas para o período selecionado
        if periodo == 'Dia':
            total_recebidas = Recebimento.query.filter(
                func.date(Recebimento.data_recebimento) == data_protocolo
            ).count()
            # Contagem de notas expedidas pelo campo data_expedicao
            total_expedidas = Expedicao.query.filter(
                func.date(Expedicao.data_expedicao) == data_protocolo
            ).count()
        elif periodo == 'Mês':
            total_recebidas = Recebimento.query.filter(
                func.strftime('%Y-%m', Recebimento.data_recebimento) == data_protocolo.strftime('%Y-%m')
            ).count()
            total_expedidas = Expedicao.query.filter(
                func.strftime('%Y-%m', Expedicao.data_expedicao) == data_protocolo.strftime('%Y-%m')
            ).count()
        elif periodo == 'Ano':
            total_recebidas = Recebimento.query.filter(
                func.strftime('%Y', Recebimento.data_recebimento) == data_protocolo.strftime('%Y')
            ).count()
            total_expedidas = Expedicao.query.filter(
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
        return redirect(url_for('protocolo'))
    return render_template('protocolo.html', usuarios=usuarios_ativos, protocolos_registrados=protocolos_registrados)

# --- Simulação de Envio de E-mail (Função Auxiliar) ---
def simular_envio_email(destinatarios, assunto, corpo):
    print(f"\n--- SIMULAÇÃO DE ENVIO DE E-MAIL ---")
    print(f"Para: {', '.join(destinatarios)}")
    print(f"Assunto: {assunto}")
    print(f"Corpo:\n{corpo}")
    print(f"-----------------------------------\n")
    # Em uma aplicação real, aqui você usaria smtplib ou uma API de e-mail.
    # requests.post('https://api.emailservice.com/send', json={'to': destinatarios, 'subject': assunto, 'body': corpo})


if __name__ == '__main__':
    app.run(debug=True)