# backend/run.py
from . import create_app # Importa a função fábrica do __init__.py

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)