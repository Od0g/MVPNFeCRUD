# routes/user_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db, Usuario

user = Blueprint('user', __name__)

# Decorador para verificar se o usuário é administrador
def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('index')) # Redireciona para o início se não for admin
        return f(*args, **kwargs)
    return decorated_function

@user.route('/cadastro', methods=['GET', 'POST'])
@admin_required # Apenas administradores podem acessar
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        matricula = request.form['matricula']
        funcao = request.form['funcao']
        email = request.form['email']
        status = request.form['status']
        perfil = request.form['perfil'] # Captura o perfil do formulário

        # Validação extra: Matricula e Email únicos
        if Usuario.query.filter_by(matricula=matricula).first():
            flash('Erro: Matrícula já cadastrada.', 'danger')
            usuarios = Usuario.query.all()
            return render_template('cadastro.html', usuarios=usuarios)
        if Usuario.query.filter_by(email=email).first():
            flash('Erro: E-mail já cadastrado.', 'danger')
            usuarios = Usuario.query.all()
            return render_template('cadastro.html', usuarios=usuarios)

        try:
            novo_usuario = Usuario(nome=nome, matricula=matricula, funcao=funcao, email=email, status=status, perfil=perfil)
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Usuário cadastrado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar usuário: {e}', 'danger')
        return redirect(url_for('user.cadastro')) # Usar blueprint.route_name
    usuarios = Usuario.query.all()
    return render_template('cadastro.html', usuarios=usuarios)