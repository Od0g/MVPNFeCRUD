from nfe_monitor import create_app
import os

# Define a pasta de armazenamento de forma segura
# (O Codeanywhere geralmente usa /home/runner/work/nome-do-workspace/nome-da-pasta-do-projeto)
current_dir = os.path.dirname(os.path.abspath(__file__))
storage_path = os.path.join(current_dir, 'storage')

# Cria a pasta de armazenamento se não existir
os.makedirs(os.path.join(storage_path, 'nfe_xmls'), exist_ok=True)
os.makedirs(os.path.join(storage_path, 'danfe_pdfs'), exist_ok=True)

# Define a variável de ambiente para que o config.py possa acessá-la
# Se você já configurou no .env, não precisaria disso aqui, mas é uma garantia
os.environ['STORAGE_PATH'] = storage_path

app = create_app()

if __name__ == '__main__':
    # No Codeanywhere, a porta pode variar, mas 5000 é comum.
    # Certifique-se de que a porta esteja aberta no workspace.
    app.run(debug=True, host='0.0.0.0', port=5000)