from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Usuario, Fornecedor, NFe, Recebimento, Expedicao
from config import Config
import xml.etree.ElementTree as ET
from datetime import datetime
import os

app = Flask(__name__, template_folder=Config.TEMPLATES_FOLDER)
app.config.from_object(Config)

# Inicializações
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Rotas de Autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('recebimento'))
    
    if request.method == 'POST':
        user = Usuario.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('recebimento'))
        flash('Credenciais inválidas', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rotas Principais
@app.route('/')
@login_required
def index():
    return redirect(url_for('recebimento'))

@app.route('/recebimento', methods=['GET', 'POST'])
@login_required
def recebimento():
    if request.method == 'POST':
        try:
            xml_file = request.files['xml_file']
            # Processamento do XML e salvamento
            # ... (implementar lógica de processamento)
            flash('NF-e recebida com sucesso', 'success')
        except Exception as e:
            flash(f'Erro: {str(e)}', 'danger')
    
    return render_template('recebimento.html')

# ... (implementar outras rotas)

if __name__ == '__main__':
    with app.app_context():
        # Criar todos os diretórios necessários
        Path(Config.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
        Path(Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')).parent.mkdir(parents=True, exist_ok=True)  # Linha nova
        
        # Criar banco de dados
        db.create_all()
        
        # Criar usuário admin padrão
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(
                username='admin',
                matricula='0000',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)