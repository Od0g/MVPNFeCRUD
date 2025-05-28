import xml.etree.ElementTree as ET
import logging
from datetime import datetime

# Configuração de logging para facilitar a depuração
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

def extrair_dados_essenciais(file):
    try:
        file.seek(0)  # Garante que o arquivo será lido do início
        tree = ET.parse(file)
        root = tree.getroot()

        # Valida se os principais elementos estão no XML
        inf_nfe = root.find('.//infNFe')
        emit = root.find('.//emit/xNome')
        ide = root.find('.//ide/dEmi')

        if inf_nfe is None or emit is None or ide is None:
            logging.error("Elementos essenciais do XML não encontrados.")
            return None

        # Extração de dados
        chave = inf_nfe.attrib.get('Id', '')
        if chave.startswith('NFe'):
            chave = chave[3:]  # Remove o prefixo 'NFe'

        fornecedor = emit.text
        data_emissao = ide.text

        # Validação de dados extraídos
        if not chave or not fornecedor or not data_emissao:
            logging.error("Dados essenciais ausentes no XML.")
            return None

        # Validação do formato da data
        try:
            data_emissao = datetime.strptime(data_emissao, "%Y-%m-%d").isoformat()
        except ValueError:
            logging.error("Formato de data inválido.")
            return None

        return {'chave': chave, 'fornecedor': fornecedor, 'data_emissao': data_emissao}

    except ET.ParseError as e:
        logging.error(f"Erro ao analisar XML: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado ao extrair dados: {str(e)}")
        return None
