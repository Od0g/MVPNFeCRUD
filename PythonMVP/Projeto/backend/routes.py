# backend/routes.py (Antigo app.py)
from flask import render_template, request, redirect, url_for, flash, send_from_directory, Blueprint
from . import db # AGORA importamos o 'db' do __init__.py
from .models import NFeRecebida, NFeExpedida # E os modelos do models.py
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# Crie um Blueprint para as rotas (opcional, mas boa prática)
# bp = Blueprint('main', __name__) # Descomente se for usar blueprints

# Funções auxiliares (ex: para validação de CNPJ/Chave de Acesso - simplificado para o MVP)
def validar_cnpj(cnpj):
    return len(cnpj) == 14 and cnpj.isdigit()

def validar_chave_acesso(chave):
    return len(chave) == 44 and chave.isdigit()

# --- Rotas (agora usarão 'app' ou 'bp' se for Blueprint) ---
# Se não for usar Blueprint, as rotas serão decoradas com @app.route
# Se for usar Blueprint, serão decoradas com @bp.route

@app.route('/') # Se não for usar blueprint
# @bp.route('/') # Se for usar blueprint
def index():
    return render_template('base.html') # Página inicial

@app.route('/recebimento', methods=['GET', 'POST']) # Se não for usar blueprint
# @bp.route('/recebimento', methods=['GET', 'POST']) # Se for usar blueprint
def recebimento():
    if request.method == 'POST':
        chave_acesso = request.form['chave_acesso']
        numero_nfe = request.form['numero_nfe']
        serie_nfe = request.form['serie_nfe']
        cnpj_fornecedor = request.form['cnpj_fornecedor']
        nome_fornecedor = request.form['nome_fornecedor']
        valor_total = float(request.form['valor_total'])
        usuario_recebimento = request.form['usuario_recebimento']
        regiao = request.form['regiao']
        cliente_responsavel = request.form['cliente_responsavel']
        qualidade_observacao = request.form['qualidade_observacao']
        validada = 'validada' in request.form
        confirmacao_recebimento_fisico = 'confirmacao_recebimento_fisico' in request.form
        
        # Lidar com upload do XML
        if 'xml_file' not in request.files:
            flash('Nenhum arquivo XML enviado.')
            return redirect(request.url)
        
        file = request.files['xml_file']
        if file.filename == '':
            flash('Nenhum arquivo XML selecionado.')
            return redirect(request.url)
        
        # Caminho de upload agora vem do app.config
        upload_folder = app.config['UPLOAD_FOLDER'] # Use app.config aqui
        
        if file and file.filename.endswith('.xml'):
            filename = secure_filename(file.filename)
            caminho_xml = os.path.join(upload_folder, filename)
            file.save(caminho_xml)
        else:
            flash('Formato de arquivo inválido. Por favor, envie um arquivo XML.')
            return redirect(request.url)

        # Validações básicas (pode ser mais robusto)
        if not validar_chave_acesso(chave_acesso):
            flash('Chave de acesso inválida.')
            return redirect(request.url)
        if not validar_cnpj(cnpj_fornecedor):
            flash('CNPJ do fornecedor inválido.')
            return redirect(request.url)

        nova_nfe_recebida = NFeRecebida(
            chave_acesso=chave_acesso,
            numero_nfe=numero_nfe,
            serie_nfe=serie_nfe,
            cnpj_fornecedor=cnpj_fornecedor,
            nome_fornecedor=nome_fornecedor,
            valor_total=valor_total,
            usuario_recebimento=usuario_recebimento,
            regiao=regiao,
            cliente_responsavel=cliente_responsavel,
            qualidade_observacao=qualidade_observacao,
            caminho_xml=caminho_xml,
            validada=validada,
            confirmacao_recebimento_fisico=confirmacao_recebimento_fisico
        )
        try:
            db.session.add(nova_nfe_recebida)
            db.session.commit()
            flash('NF-e recebida registrada com sucesso!')
            return redirect(url_for('recebimento'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar NF-e recebida: {e}')
            print(f"Erro ao registrar NFe Recebida: {e}") # Para depuração
            return redirect(request.url)

    nfe_recebidas = NFeRecebida.query.order_by(NFeRecebida.data_hora_recebimento.desc()).all()
    return render_template('recebimento.html', nfe_recebidas=nfe_recebidas)

@app.route('/expedicao', methods=['GET', 'POST']) # Se não for usar blueprint
# @bp.route('/expedicao', methods=['GET', 'POST']) # Se for usar blueprint
def expedicao():
    if request.method == 'POST':
        chave_acesso = request.form['chave_acesso']
        numero_nfe = request.form['numero_nfe']
        serie_nfe = request.form['serie_nfe']
        cnpj_cliente = request.form['cnpj_cliente']
        nome_cliente = request.form['nome_cliente']
        valor_total = float(request.form['valor_total'])
        usuario_emissor = request.form['usuario_emissor']
        regiao = request.form['regiao']
        qualidade_observacao = request.form['qualidade_observacao']
        status_sefaz = request.form['status_sefaz']

        # Lidar com upload do XML
        if 'xml_file' not in request.files:
            flash('Nenhum arquivo XML enviado.')
            return redirect(request.url)
        
        file = request.files['xml_file']
        if file.filename == '':
            flash('Nenhum arquivo XML selecionado.')
            return redirect(request.url)
        
        upload_folder = app.config['UPLOAD_FOLDER'] # Use app.config aqui
        
        if file and file.filename.endswith('.xml'):
            filename = secure_filename(file.filename)
            caminho_xml = os.path.join(upload_folder, filename)
            file.save(caminho_xml)
        else:
            flash('Formato de arquivo inválido. Por favor, envie um arquivo XML.')
            return redirect(request.url)

        # Validações básicas
        if not validar_chave_acesso(chave_acesso):
            flash('Chave de acesso inválida.')
            return redirect(request.url)
        if not validar_cnpj(cnpj_cliente):
            flash('CNPJ do cliente inválido.')
            return redirect(request.url)

        nova_nfe_expedida = NFeExpedida(
            chave_acesso=chave_acesso,
            numero_nfe=numero_nfe,
            serie_nfe=serie_nfe,
            cnpj_cliente=cnpj_cliente,
            nome_cliente=nome_cliente,
            valor_total=valor_total,
            usuario_emissor=usuario_emissor,
            regiao=regiao,
            qualidade_observacao=qualidade_observacao,
            caminho_xml=caminho_xml,
            status_sefaz=status_sefaz
        )
        try:
            db.session.add(nova_nfe_expedida)
            db.session.commit()
            flash('NF-e expedida registrada com sucesso!')
            return redirect(url_for('expedicao'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar NF-e expedida: {e}')
            print(f"Erro ao registrar NFe Expedida: {e}") # Para depuração
            return redirect(request.url)

    nfe_expedidas = NFeExpedida.query.order_by(NFeExpedida.data_hora_emissao.desc()).all()
    return render_template('expedicao.html', nfe_expedidas=nfe_expedidas)

@app.route('/relatorio')
def relatorio():
    recebidas = NFeRecebida.query.all()
    expedidas = NFeExpedida.query.all()
    return render_template('relatorio.html', recebidas=recebidas, expedidas=expedidas)

@app.route('/view_nfe/<string:nfe_type>/<int:nfe_id>')
def view_nfe(nfe_type, nfe_id):
    if nfe_type == 'recebida':
        nfe = NFeRecebida.query.get_or_404(nfe_id)
    elif nfe_type == 'expedida':
        nfe = NFeExpedida.query.get_or_404(nfe_id)
    else:
        flash('Tipo de NF-e inválido.')
        return redirect(url_for('index'))
    
    return render_template('view.html', nfe=nfe, nfe_type=nfe_type)

@app.route('/download_xml/<string:nfe_type>/<int:nfe_id>')
def download_xml(nfe_type, nfe_id):
    if nfe_type == 'recebida':
        nfe = NFeRecebida.query.get_or_404(nfe_id)
    elif nfe_type == 'expedida':
        nfe = NFeExpedida.query.get_or_404(nfe_id)
    else:
        flash('Tipo de NF-e inválido.')
        return redirect(url_for('index'))
    
    # Extrai o diretório e o nome do arquivo do caminho_xml
    directory = os.path.dirname(nfe.caminho_xml)
    filename = os.path.basename(nfe.caminho_xml)
    
    return send_from_directory(directory=directory, path=filename, as_attachment=True)


@app.route('/edit_recebimento/<int:id>', methods=['GET', 'POST'])
def edit_recebimento(id):
    nfe = NFeRecebida.query.get_or_404(id)
    if request.method == 'POST':
        nfe.chave_acesso = request.form['chave_acesso']
        nfe.numero_nfe = request.form['numero_nfe']
        nfe.serie_nfe = request.form['serie_nfe']
        nfe.cnpj_fornecedor = request.form['cnpj_fornecedor']
        nfe.nome_fornecedor = request.form['nome_fornecedor']
        nfe.valor_total = float(request.form['valor_total'])
        nfe.usuario_recebimento = request.form['usuario_recebimento']
        nfe.regiao = request.form['regiao']
        nfe.cliente_responsavel = request.form['cliente_responsavel']
        nfe.qualidade_observacao = request.form['qualidade_observacao']
        nfe.validada = 'validada' in request.form
        nfe.confirmacao_recebimento_fisico = 'confirmacao_recebimento_fisico' in request.form

        if 'xml_file' in request.files and request.files['xml_file'].filename != '':
            file = request.files['xml_file']
            upload_folder = app.config['UPLOAD_FOLDER'] # Use app.config aqui
            if file and file.filename.endswith('.xml'):
                if os.path.exists(nfe.caminho_xml):
                    os.remove(nfe.caminho_xml)
                filename = secure_filename(file.filename)
                caminho_xml = os.path.join(upload_folder, filename)
                file.save(caminho_xml)
                nfe.caminho_xml = caminho_xml
            else:
                flash('Formato de arquivo inválido para o XML. Manter arquivo anterior.')
                return redirect(request.url)
        
        try:
            db.session.commit()
            flash('NF-e recebida atualizada com sucesso!')
            return redirect(url_for('recebimento'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar NF-e recebida: {e}')
            print(f"Erro ao atualizar NFe Recebida: {e}")
            return redirect(request.url)
            
    return render_template('edit_recebimento.html', nfe=nfe)

@app.route('/delete_recebimento/<int:id>', methods=['POST'])
def delete_recebimento(id):
    nfe = NFeRecebida.query.get_or_404(id)
    try:
        if os.path.exists(nfe.caminho_xml):
            os.remove(nfe.caminho_xml)
        db.session.delete(nfe)
        db.session.commit()
        flash('NF-e recebida excluída com sucesso!')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir NF-e recebida: {e}')
        print(f"Erro ao excluir NFe Recebida: {e}")
    return redirect(url_for('recebimento'))

# Remova o bloco if __name__ == '__main__': daqui
# Ele será no run.py agora