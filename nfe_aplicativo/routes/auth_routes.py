# routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from database import db, Usuario

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index')) # Já logado, redireciona para a página inicial

    if request.method == 'POST':
        matricula = request.form['matricula']
        # No mundo real, você usaria uma senha e a hashificaria!
        # Por simplicidade, vamos usar a matrícula como "senha" ou deixar sem senha por enquanto.
        # Usuario.query.filter_by(matricula=matricula, senha_hash=hash(senha)).first()
        usuario = Usuario.query.filter_by(matricula=matricula).first()

        if usuario:
            login_user(usuario)
            flash(f'Bem-vindo, {usuario.nome}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Matrícula inválida. Verifique e tente novamente.', 'danger')
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('auth.login'))