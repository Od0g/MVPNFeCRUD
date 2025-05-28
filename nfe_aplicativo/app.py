# app.py
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from database import db, Usuario
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Define para onde redirecionar se não estiver logado
    login_manager.login_message = "Por favor, faça login para acessar esta página."
    login_manager.login_message_category = "danger"

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    with app.app_context():
        db.create_all()

        # Importar e registrar blueprints
        from routes.auth_routes import auth as auth_bp
        from routes.user_routes import user as user_bp
        from routes.nfe_routes import nfe as nfe_bp
        from routes.report_routes import report as report_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(user_bp)
        app.register_blueprint(nfe_bp)
        app.register_blueprint(report_bp)

    @app.route('/')
    @login_required # Somente usuários logados podem acessar a página inicial
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)