from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    from .routes import auth, nfe, operacao
    app.register_blueprint(auth.bp)
    app.register_blueprint(nfe.bp)
    app.register_blueprint(operacao.bp)

    # Você pode ter uma rota raiz simples aqui, por exemplo:
    @app.route('/')
    def home():
        return render_template('login.html')

    return app
