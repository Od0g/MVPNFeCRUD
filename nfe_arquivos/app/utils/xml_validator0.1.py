import xml.etree.ElementTree as ET

def extrair_dados_essenciais(file):
    try:
        file.seek(0)
        tree = ET.parse(file)
        root = tree.getroot()

        # Exemplo simples (ajuste conforme seu XML)
        chave = root.find('.//infNFe').attrib.get('Id', '')[3:]  # remove 'NFe' prefix
        fornecedor = root.find('.//emit/xNome').text
        data_emissao = root.find('.//ide/dEmi').text

        if not chave or not fornecedor or not data_emissao:
            return None

        return {'chave': chave, 'fornecedor': fornecedor, 'data_emissao': data_emissao}
    except Exception:
        return None
