from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db, Usuario, Recebimento, Expedicao, Protocolo
import datetime
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased
import requests # Para simular envio de e-mail

# Imports para Flask-Login
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gerenciador_nfe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'uma_chave_secreta_muito_segura_para_flash_messages_e_sessoes' # Chave para sessões e flash

db.init_app(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Rota para onde usuários não logados são redirecionados
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Cria as tabelas do banco de dados se não existirem
with app.app_context():
    db.create_all()

# --- Rotas de Autenticação ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        matricula = request.form['matricula']
        password = request.form['password']
        usuario = Usuario.query.filter_by(matricula=matricula).first()
        if usuario and usuario.check_password(password):
            if usuario.status == 'Ativo':
                login_user(usuario)
                flash('Login bem-sucedido!', 'success')
                # Redireciona para a próxima página solicitada ou para o index
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            else:
                flash('Usuário inativo. Contate o administrador.', 'warning')
        else:
            flash('Matrícula ou senha inválida.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required # Só pode deslogar se estiver logado
def logout():
    logout_user()
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('login'))


# --- Rotas da Aplicação (Protegidas) ---

@app.route('/')
@login_required # Proteger a rota principal
def index():
    return render_template('index.html')

## Aba: Cadastro
# A rota de cadastro pode ser acessível para criar o primeiro usuário ou por administradores.
# Se for para qualquer um se cadastrar, pode não precisar de @login_required aqui,
# mas o acesso às funcionalidades após cadastro sim.
# Por ora, vamos manter o cadastro acessível para criar usuários.
# Se a intenção é que SÓ usuários logados (ex: admins) possam cadastrar outros, adicione @login_required.
@app.route('/cadastro', methods=['GET', 'POST'])
@login_required # Exigir login para cadastrar novos usuários
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        matricula = request.form['matricula']
        funcao = request.form['funcao']
        email = request.form['email']
        password = request.form['password'] # Novo campo de senha
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
                novo_usuario.set_password(password) # Salvar a senha com hash
                db.session.add(novo_usuario)
                db.session.commit()
                flash('Usuário cadastrado com sucesso!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao cadastrar usuário: {e}', 'danger')
            return redirect(url_for('cadastro')) # Redirecionar após POST

    usuarios = Usuario.query.all()
    return render_template('cadastro.html', usuarios=usuarios)


## Aba: Recebimento
@app.route('/recebimento', methods=['GET', 'POST'])
@login_required # Proteger
def recebimento():
    # Usuários ativos para o formulário
    usuarios_ativos = Usuario.query.filter_by(status='Ativo').all()
    if request.method == 'POST':
        responsavel_entrega = request.form['responsavel_entrega']
        responsavel_recebimento_id = request.form['responsavel_recebimento']
        fornecedor = request.form['fornecedor']
        chave_nfe = request.form['chave_nfe']
        numero_nfe = request.form['numero_nfe']
        turno = request.form['turno']

        # Validação para garantir que o usuário selecionado existe e está ativo
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
                status='Pendente',
                turno=turno
            )
            db.session.add(novo_recebimento)
            db.session.commit()

            destinatarios = ['financeiro@empresa.com', 'augusto_inacio@lslgr.com.br', 'compras@empresa.com']
            nfe_info = f"NF-e {numero_nfe} (Chave: {chave_nfe}) do fornecedor {fornecedor}"
            simular_envio_email(destinatarios, "Recebimento de NF-e", f"Uma nova NF-e foi recebida: {nfe_info} por {responsavel_obj.nome}")
            flash('Recebimento registrado e e-mail simulado enviado com sucesso!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar recebimento: {e}', 'danger')
        return redirect(url_for('recebimento'))
    return render_template('recebimento.html', usuarios=usuarios_ativos)


## Aba: Expedição
@app.route('/expedicao', methods=['GET', 'POST'])
@login_required # Proteger
def expedicao():
    usuarios_ativos = Usuario.query.filter_by(status='Ativo').all()
    recebimentos_pendentes = Recebimento.query.filter_by(status='Pendente').all()

    if request.method == 'POST':
        recebimento_id = request.form['recebimento_id']
        responsavel_entrega_expedicao = request.form['responsavel_entrega_expedicao']
        responsavel_recebimento_expedicao_id = request.form['responsavel_recebimento_expedicao']
        turno = request.form['turno']

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
            nova_expedicao = Expedicao(
                recebimento_id=recebimento_id,
                responsavel_entrega_expedicao=responsavel_entrega_expedicao,
                responsavel_recebimento_expedicao_id=responsavel_recebimento_expedicao_id,
                turno=turno
            )
            db.session.add(nova_expedicao)
            recebimento_associado.status = 'Concluído'
            db.session.commit()

            destinatarios = ['logistica@empresa.com', 'cliente@empresa.com']
            nfe_info = f"NF-e {recebimento_associado.numero_nfe} (Chave: {recebimento_associado.chave_nfe}) foi expedida por {responsavel_obj.nome}."
            simular_envio_email(destinatarios, "Expedição de NF-e", f"Uma NF-e foi expedida: {nfe_info}")
            flash('Expedição registrada e recebimento atualizado com sucesso!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar expedição: {e}', 'danger')
        return redirect(url_for('expedicao'))
    return render_template('expedicao.html', usuarios=usuarios_ativos, recebimentos_pendentes=recebimentos_pendentes)


## Aba: Relatório
@app.route('/relatorio')
@login_required # Proteger
def relatorio():
    Usuario_exp = aliased(Usuario)
    # ... (resto do seu código de relatório)
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
     .order_by(Recebimento.data_recebimento.desc())\
     .all()

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

    meses_ordenados = sorted(mensal_data.keys())
    labels_meses = [datetime.datetime.strptime(m, '%Y-%m').strftime('%b/%Y') for m in meses_ordenados]
    data_recebidas_mensal = [mensal_data[m]['recebidas'] for m in meses_ordenados]
    data_expedidas_mensal = [mensal_data[m]['expedidas'] for m in meses_ordenados]

    total_pendentes = Recebimento.query.filter_by(status='Pendente').count()
    total_concluidas = Recebimento.query.filter_by(status='Concluído').count()

    return render_template('relatorio.html',
                           dados_relatorio=dados_relatorio,
                           labels_meses=labels_meses,
                           data_recebidas_mensal=data_recebidas_mensal,
                           data_expedidas_mensal=data_expedidas_mensal,
                           total_pendentes=total_pendentes,
                           total_concluidas=total_concluidas)


## Aba: Protocolo
@app.route('/protocolo', methods=['GET', 'POST'])
@login_required # Proteger
def protocolo():
    usuarios_ativos = Usuario.query.filter_by(status='Ativo').all()
    protocolos_registrados = Protocolo.query.order_by(Protocolo.data_protocolo.desc()).all()

    if request.method == 'POST':
        data_protocolo_str = request.form['data_protocolo']
        periodo = request.form['periodo']
        responsavel_protocolo_id = request.form['responsavel_protocolo']
        observacoes = request.form['observacoes']

        responsavel_obj = Usuario.query.get(responsavel_protocolo_id)
        if not responsavel_obj or responsavel_obj.status != 'Ativo':
            flash('Responsável pelo protocolo inválido ou inativo.', 'danger')
            return redirect(url_for('protocolo'))

        try:
            data_protocolo = datetime.datetime.strptime(data_protocolo_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data do protocolo inválida.', 'danger')
            return redirect(url_for('protocolo'))

        # Contagem de notas para o período selecionado
        # ... (sua lógica de contagem de notas existente)
        if periodo == 'Dia':
            total_recebidas = Recebimento.query.filter(
                func.date(Recebimento.data_recebimento) == data_protocolo
            ).count()
            total_expedidas = db.session.query(Expedicao).join(Recebimento).filter(
                # Para expedição, usamos a data da expedição, não do recebimento original
                func.date(Expedicao.data_expedicao) == data_protocolo
            ).count()
        elif periodo == 'Mês':
            mes_ano_str = data_protocolo.strftime('%Y-%m')
            total_recebidas = Recebimento.query.filter(
                func.strftime('%Y-%m', Recebimento.data_recebimento) == mes_ano_str
            ).count()
            total_expedidas = db.session.query(Expedicao).filter( # Não precisa do join para contar expedições do mês
                func.strftime('%Y-%m', Expedicao.data_expedicao) == mes_ano_str
            ).count()
        elif periodo == 'Ano':
            ano_str = data_protocolo.strftime('%Y')
            total_recebidas = Recebimento.query.filter(
                func.strftime('%Y', Recebimento.data_recebimento) == ano_str
            ).count()
            total_expedidas = db.session.query(Expedicao).filter(
                func.strftime('%Y', Expedicao.data_expedicao) == ano_str
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

if __name__ == '__main__':
    app.run(debug=True)