from lxml import etree

def extrair_dados_essenciais(xml_file):
    try:
        tree = etree.parse(xml_file)
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        chave = tree.findtext('.//nfe:infNFe', namespaces=ns)
        if chave:
            chave = chave.strip()

        emitente = tree.findtext('.//nfe:emit/nfe:xNome', namespaces=ns)
        data_emissao = tree.findtext('.//nfe:ide/nfe:dhEmi', namespaces=ns)
        
        return {
            'chave': chave,
            'fornecedor': emitente,
            'data_emissao': data_emissao
        }
    except Exception as e:
        print(f"Erro na validação do XML: {e}")
        return None
