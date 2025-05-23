# backend/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

db = SQLAlchemy()
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'nfe_xmls')

def create_app():
    app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
    app.config.from_object(Config)

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db.init_app(app)

    with app.app_context():
        from . import models # Importa o módulo models para que as classes sejam registradas
        db.create_all() # Cria as tabelas

    from . import routes # Importa o módulo de rotas
    # Para que as rotas sejam registradas no app, precisamos de um jeito.
    # A forma mais limpa é usar blueprints, mas para manter simples,
    # você pode passar o 'app' para as funções de rota ou ter um registro direto.
    # Se você definiu as rotas com @app.route em routes.py, então a importação basta.
    # No entanto, para evitar importações cíclicas entre __init__.py e routes.py
    # onde routes.py precisa de 'app' e '__init__.py' importa 'routes',
    # o melhor é passar o app ou usar blueprints.

    # *** Vamos ajustar routes.py para não ter 'app' global e usar Blueprint. ***
    # Isso é mais robusto para a estrutura de pacote.
    # Para fazer isso, no routes.py, você vai importar Blueprint e criar bp = Blueprint(...)
    # e decorar as rotas com @bp.route.
    # Então, aqui, você registrará o blueprint.

    # Remova o 'app' global de routes.py e use Blueprint:
    # from .routes import bp # Importa o Blueprint
    # app.register_blueprint(bp) # Registra o Blueprint

    # Se você *não* quiser usar Blueprints agora, podemos fazer a importação das rotas
    # de forma que as rotas sejam "vistas" e adicionadas ao app sem um blueprint.
    # O problema é que routes.py também importa 'db' e 'models',
    # e se 'routes.py' também tentar importar 'app', voltamos à circularidade.

    # A forma mais simples SEM Blueprint para o seu caso, assumindo que `routes.py`
    # só importa `db` e `models` e não `app` globalmente, é que ao importar `routes`
    # as funções decoradas com `@app.route` se registrem.
    # Mas isso requer que 'app' esteja disponível como uma variável global no routes.py.
    # A solução com factory elimina isso.

    # Então, o mais seguro é que 'routes.py' importe 'db' de '.' e os modelos de '.models'.
    # E que as rotas sejam decoradas com `@app.route` globalmente no routes.py.
    # Para que 'app' esteja disponível em routes.py, precisaria ser passado ou importado.

    # OK, vamos voltar à estrutura mais simples com a factory e sem Blueprint para o MVP.
    # A importação das rotas diretamente:
    from . import routes # Isso fará com que as funções @app.route em routes.py se registrem no 'app'.

    return app