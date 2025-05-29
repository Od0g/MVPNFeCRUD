# api/index.py
import sys
import os

# Adiciona o diretório pai ao PATH para que o Flask consiga encontrar os outros módulos
# Isso é crucial para a Vercel, pois o 'api' está em um subdiretório
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from app import create_app
from database import db # Importar db para criar as tabelas se necessário

app = create_app()

# Este bloco tenta criar as tabelas no DB SQLite
# Lembre-se: em Vercel, este DB não será persistente!
with app.app_context():
    db.create_all()

# Para fins de deploy na Vercel, o Flask precisa ser 'exportado' como `app`
# A Vercel vai procurar por um objeto 'app' neste arquivo.