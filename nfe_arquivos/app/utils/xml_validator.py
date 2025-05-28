import xml.etree.ElementTree as ET
import logging
from datetime import datetime

logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

def extrair_dados_essenciais(file):
    try:
        file.seek(0)
        tree = ET.parse(file)
        root = tree.getroot()

        # Captura o namespace
        ns = {"ns": "http://www.portalfiscal.inf.br/nfe"}

        # Busca os elementos considerando o namespace
        inf_nfe = root.find(".//ns:infNFe", ns)
        emit = root.find(".//ns:emit/ns:xNome", ns)
        ide = root.find(".//ns:ide/ns:dhEmi", ns)

        if inf_nfe is None or emit is None or ide is None:
            logging.error("Elementos essenciais do XML não encontrados.")
            return None

        # Extração de dados
        chave = inf_nfe.attrib.get("Id", "")
        if chave.startswith("NFe"):
            chave = chave[3:]  # Remove o prefixo 'NFe' da chave

        fornecedor = emit.text
        data_emissao = ide.text

        # Ajuste na conversão de data para ISO format
        try:
            data_emissao = datetime.strptime(data_emissao[:10], "%Y-%m-%d").isoformat()
        except ValueError:
            logging.error("Formato de data inválido.")
            return None

        return {"chave": chave, "fornecedor": fornecedor, "data_emissao": data_emissao}

    except ET.ParseError as e:
        logging.error(f"Erro ao analisar XML: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado ao extrair dados: {str(e)}")
        return None
