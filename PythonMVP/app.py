from flask import Flask, render_template, request, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nfe.db'
app.config['UPLOAD_FOLDER'] = 'nfe_arquivos'
db = SQLAlchemy(app)

class NFe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(44), unique=True, nullable=False)
    emitente = db.Column(db.String(100), nullable=False)
    destinatario = db.Column(db.String(100), nullable=False)
    data_emissao = db.Column(db.DateTime, nullable=False)
    arquivo_path = db.Column(db.String(200), nullable=False)
    data_recebimento = db.Column(db.DateTime, default=datetime.now)

@app.route('/')
def index():
    nfes = NFe.query.all()
    return render_template('index.html', nfes=nfes)

@app.route('/upload', methods=['POST'])
def upload():
    if 'xml_file' not in request.files:
        return redirect('/')
    
    file = request.files['xml_file']
    if file.filename == '':
        return redirect('/')
    
    try:
        # Validar XML básico
        tree = ET.parse(file.stream)
        root = tree.getroot()
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        chave = root.find('.//nfe:infNFe', ns).attrib['Id'][3:]
        emitente = root.find('.//nfe:emit/nfe:xNome', ns).text
        destinatario = root.find('.//nfe:dest/nfe:xNome', ns).text
        data_emissao = datetime.strptime(root.find('.//nfe:dhEmi', ns).text[:19], '%Y-%m-%dT%H:%M:%S')
        
        # Salvar arquivo
        filename = f"{chave}.xml"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.seek(0)
        file.save(file_path)
        
        # Salvar no banco
        nfe = NFe(
            chave=chave,
            emitente=emitente,
            destinatario=destinatario,
            data_emissao=data_emissao,
            arquivo_path=file_path
        )
        db.session.add(nfe)
        db.session.commit()
        
    except Exception as e:
        print(f"Erro: {str(e)}")
    
    return redirect('/')

@app.route('/download/<int:id>')
def download(id):
    nfe = NFe.query.get(id)
    return send_from_directory(os.path.dirname(nfe.arquivo_path), os.path.basename(nfe.arquivo_path))

@app.route('/delete/<int:id>')
def delete(id):
    nfe = NFe.query.get(id)
    if os.path.exists(nfe.arquivo_path):
        os.remove(nfe.arquivo_path)
    db.session.delete(nfe)
    db.session.commit()
    return redirect('/')


@app.route('/view/<int:id>')
def view_nfe(id):
    nfe = NFe.query.get(id)
    
    try:
        tree = ET.parse(nfe.arquivo_path)
        root = tree.getroot()
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        # Extrair mais dados
        detalhes = {
            'emitente': {
                'nome': root.find('.//nfe:emit/nfe:xNome', ns).text,
                'cnpj': root.find('.//nfe:emit/nfe:CNPJ', ns).text,
                'endereco': {
                    'logradouro': root.find('.//nfe:emit/nfe:enderEmit/nfe:xLgr', ns).text,
                    'numero': root.find('.//nfe:emit/nfe:enderEmit/nfe:nro', ns).text,
                    'cidade': root.find('.//nfe:emit/nfe:enderEmit/nfe:xMun', ns).text,
                    'uf': root.find('.//nfe:emit/nfe:enderEmit/nfe:UF', ns).text
                }
            },
            'destinatario': {
                'nome': root.find('.//nfe:dest/nfe:xNome', ns).text,
                'cnpj': root.find('.//nfe:dest/nfe:CNPJ', ns).text,
                'endereco': {
                    'logradouro': root.find('.//nfe:dest/nfe:enderDest/nfe:xLgr', ns).text,
                    'numero': root.find('.//nfe:dest/nfe:enderDest/nfe:nro', ns).text,
                    'cidade': root.find('.//nfe:dest/nfe:enderDest/nfe:xMun', ns).text,
                    'uf': root.find('.//nfe:dest/nfe:enderDest/nfe:UF', ns).text
                }
            },
            'produtos': [],
            'total': {
                'valor': root.find('.//nfe:total/nfe:ICMSTot/nfe:vNF', ns).text
            }
        }
        
        # Extrair produtos
        for item in root.findall('.//nfe:det', ns):
            prod = {
                'descricao': item.find('.//nfe:prod/nfe:xProd', ns).text,
                'quantidade': item.find('.//nfe:prod/nfe:qCom', ns).text,
                'unidade': item.find('.//nfe:prod/nfe:uCom', ns).text,
                'valor_unitario': item.find('.//nfe:prod/nfe:vUnCom', ns).text,
                'valor_total': item.find('.//nfe:prod/nfe:vProd', ns).text
            }
            detalhes['produtos'].append(prod)
            
        return render_template('view.html', nfe=nfe, detalhes=detalhes)
        
    except Exception as e:
        return f"Erro ao ler XML: {str(e)}"



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)