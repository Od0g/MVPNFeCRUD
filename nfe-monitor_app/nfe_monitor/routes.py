from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from werkzeug.utils import secure_filename
from . import db
from .models import NFe
from .services.xml_parser import NFeParser
import os
import pandas as pd
from datetime import datetime

main_bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main_bp.route('/')
def index():
    # Ordena as notas pela data de recebimento (upload) em ordem decrescente
    notes = NFe.query.order_by(NFe.data_recebimento.desc()).all()
    return render_template('index.html', notes=notes)

@main_bp.route('/upload', methods=['GET', 'POST'])
def upload_nfe():
    if request.method == 'POST':
        if 'xml_file' not in request.files:
            flash('Nenhum arquivo enviado.', 'danger')
            return redirect(request.url)
        
        file = request.files['xml_file']
        
        if file.filename == '':
            flash('Nenhum arquivo selecionado.', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Estrutura de pasta para armazenamento (CNPJ/ANO/MES) - SIMPLIFICADA
            # No protótipo, vamos usar uma pasta única por simplicidade.
            # Em produção, usaria NFe.emitente_cnpj, ano=data.year, mes=data.month
            
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'nfe_xmls')
            os.makedirs(upload_dir, exist_ok=True) # Garante que a pasta existe

            file_path = os.path.join(upload_dir, filename)
            
            # Verifica se a chave de acesso já existe para evitar duplicatas
            try:
                parser = NFeParser(file.stream) # Passa o stream diretamente para o parser
                nfe_data = parser.parse()
                
                # Validação da assinatura (simulada)
                if not parser.validate_signature():
                    flash(f'Validação de assinatura falhou para {filename}.', 'warning')
                    # Você pode decidir parar o processo aqui ou apenas avisar
                    
                existing_nfe = NFe.query.filter_by(chave_acesso=nfe_data['chave_acesso']).first()
                if existing_nfe:
                    flash(f'NF-e com chave de acesso {nfe_data["chave_acesso"]} já existe.', 'info')
                    return redirect(url_for('main.index'))

                # Salva o arquivo XML fisicamente
                file.stream.seek(0) # Retorna o ponteiro do stream para o início antes de salvar
                file.save(file_path)

                new_nfe = NFe(
                    chave_acesso=nfe_data['chave_acesso'],
                    numero=nfe_data['numero'],
                    emitente_cnpj=nfe_data['emitente_cnpj'],
                    emitente_nome=nfe_data['emitente_nome'],
                    destinatario_cnpj=nfe_data['destinatario_cnpj'],
                    destinatario_nome=nfe_data['destinatario_nome'],
                    valor_total=nfe_data['valor_total'],
                    data_emissao=nfe_data['data_emissao'],
                    xml_filename=filename
                )
                db.session.add(new_nfe)
                db.session.commit()
                flash(f'NF-e {filename} enviada e processada com sucesso!', 'success')
            except Exception as e:
                flash(f'Erro ao processar NF-e {filename}: {e}', 'danger')
                # Tenta remover o arquivo se o processamento falhou
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            return redirect(url_for('main.index'))
        else:
            flash('Tipo de arquivo não permitido.', 'danger')
    return render_template('upload.html')

@main_bp.route('/nfe/<int:nfe_id>')
def nfe_detail(nfe_id):
    nfe = NFe.query.get_or_404(nfe_id)
    return render_template('nfe_detail.html', nfe=nfe)

@main_bp.route('/nfe/<int:nfe_id>/edit', methods=['GET', 'POST'])
def edit_nfe(nfe_id):
    nfe = NFe.query.get_or_404(nfe_id)
    if request.method == 'POST':
        nfe.status = request.form['status']
        nfe.responsavel_recebimento = request.form.get('responsavel_recebimento')
        nfe.turno_recebimento = request.form.get('turno_recebimento')
        
        try:
            nfe.quantidade_itens = int(request.form.get('quantidade_itens')) if request.form.get('quantidade_itens') else None
        except ValueError:
            flash('Quantidade de itens deve ser um número inteiro.', 'danger')
            return redirect(url_for('main.edit_nfe', nfe_id=nfe.id))

        nfe.destino_expedicao = request.form.get('destino_expedicao')
        nfe.responsavel_expedicao = request.form.get('responsavel_expedicao')
        nfe.email_responsavel_entrega = request.form.get('email_responsavel_entrega')

        if nfe.status == 'Expedida' and not nfe.data_expedicao:
            nfe.data_expedicao = datetime.utcnow()
        elif nfe.status != 'Expedida':
            nfe.data_expedicao = None # Limpa a data se o status mudar

        db.session.commit()
        flash('NF-e atualizada com sucesso!', 'success')
        return redirect(url_for('main.nfe_detail', nfe_id=nfe.id))
    
    return render_template('nfe_form.html', nfe=nfe)

@main_bp.route('/download_xml/<int:nfe_id>')
def download_xml(nfe_id):
    nfe = NFe.query.get_or_404(nfe_id)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'nfe_xmls', nfe.xml_filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=nfe.xml_filename)
    flash('Arquivo XML não encontrado.', 'danger')
    return redirect(url_for('main.nfe_detail', nfe_id=nfe.id))

@main_bp.route('/reports/csv')
def generate_csv_report():
    # Consulta todos os dados de NFe
    all_nfe = NFe.query.all()
    
    # Prepara os dados para o DataFrame
    data = []
    for nfe in all_nfe:
        data.append({
            'Chave de Acesso': nfe.chave_acesso,
            'Número NF-e': nfe.numero,
            'Emitente CNPJ': nfe.emitente_cnpj,
            'Emitente Nome': nfe.emitente_nome,
            'Destinatário CNPJ': nfe.destinatario_cnpj,
            'Destinatário Nome': nfe.destinatario_nome,
            'Valor Total': nfe.valor_total,
            'Data Emissão': nfe.data_emissao.strftime('%Y-%m-%d %H:%M:%S'),
            'Data Recebimento (Upload)': nfe.data_recebimento.strftime('%Y-%m-%d %H:%M:%S'),
            'Status': nfe.status,
            'Responsável Recebimento': nfe.responsavel_recebimento,
            'Turno Recebimento': nfe.turno_recebimento,
            'Quantidade Itens': nfe.quantidade_itens,
            'Destino Expedição': nfe.destino_expedicao,
            'Responsável Expedição': nfe.responsavel_expedicao,
            'Data Expedição': nfe.data_expedicao.strftime('%Y-%m-%d %H:%M:%S') if nfe.data_expedicao else '',
            'Email Responsável Entrega': nfe.email_responsavel_entrega
        })

    if not data:
        flash('Nenhuma NF-e para gerar relatório.', 'info')
        return redirect(url_for('main.index'))

    df = pd.DataFrame(data)
    
    # Salva para um arquivo CSV temporário
    csv_filename = 'relatorio_nfe.csv'
    csv_path = os.path.join(current_app.root_path, csv_filename) # Salva temporariamente na raiz da app
    df.to_csv(csv_path, index=False, encoding='utf-8-sig', sep=';') # Use sep=';' para Excel em pt-BR

    return send_file(csv_path, as_attachment=True, download_name=csv_filename, mimetype='text/csv')