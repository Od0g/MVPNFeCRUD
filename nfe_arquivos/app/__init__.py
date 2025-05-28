from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config
import os

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # cria pasta uploads se não existir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)

    from .routes import auth, nfe, operacao
    app.register_blueprint(auth.bp)
    app.register_blueprint(nfe.bp)
    app.register_blueprint(operacao.bp)

    @app.route('/')
    def index():
        return render_template('login.html')

    @app.route('/nfe/gestao')
    def gestao_nfe():
        return render_template('gestao_nfe.html')

    @app.route('/operacao')
    def operacao_index():
        return render_template('operacao.html')

    @app.route('/relatorios')
    def relatorios():
        from app.models import NFeOperacao
        # Exemplo de consulta com filtros
        operacoes = NFeOperacao.query.all()
        return render_template('relatorios.html', operacoes=operacoes)
    

    @app.route('/register-manual')  # Corrigido aqui
    def register_manual():
        from app.models import User
        if User.query.filter_by(username='admin').first():
            return 'Usuário admin já existe'
        user = User(username='admin', role='admin')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        return 'Usuário admin criado'

    with app.app_context():
        db.create_all()

    return app
