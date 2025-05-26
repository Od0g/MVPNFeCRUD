from flask import Flask
from dotenv import load_dotenv
import os
from .extensions import db  # Agora importa de extensions.py

load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Config')
    app.config.from_pyfile('config.py', silent=True)

    db.init_app(app)

    with app.app_context():
        from . import models  # Importa modelos dentro do contexto da app
        db.create_all()

    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
