# init_db.py

from nfe_monitor import create_app, db

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Banco de dados criado com sucesso!")
