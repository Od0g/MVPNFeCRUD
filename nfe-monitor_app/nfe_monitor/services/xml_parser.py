import xml.etree.ElementTree as ET
import os
from datetime import datetime

class NFeParser:
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.tree = ET.parse(xml_path)
        self.root = self.tree.getroot()
        # Namespaces comuns da NF-e
        self.ns = {
            'nfe': 'http://www.portalfiscal.inf.br/nfe',
            'ns': 'http://www.portalfiscal.inf.br/nfe' # Algumas vezes a tag raiz usa 'ns'
        }

    def _find_text(self, xpath, default='N/A'):
        # Tenta encontrar o elemento com os namespaces definidos
        element = self.root.find(xpath, self.ns)
        if element is None:
            # Tenta sem namespace se a primeira tentativa falhar (compatibilidade)
            element = self.root.find(xpath.split(':')[-1]) # Pega o nome da tag sem o prefixo
        return element.text if element is not None else default

    def parse(self):
        try:
            chave_acesso = self._find_text('.//nfe:chNFe')
            if chave_acesso == 'N/A': # Tenta outra forma se a primeira falhar
                chave_acesso_alt = self._find_text('.//infNFe')
                if chave_acesso_alt != 'N/A' and 'Id' in self.root.attrib:
                    chave_acesso = self.root.attrib['Id'][3:] # Remove 'NFe' do início

            numero = self._find_text('.//nfe:nNF')
            valor_total = float(self._find_text('.//nfe:vNF')) if self._find_text('.//nfe:vNF') != 'N/A' else 0.0

            # Datas podem vir em diferentes formatos
            data_emissao_str = self._find_text('.//nfe:dhEmi')
            if data_emissao_str == 'N/A':
                data_emissao_str = self._find_text('.//nfe:dEmi') # Formato mais antigo
            
            # Tenta parsear a data, se falhar, usa a data atual
            try:
                # Tenta formatos comuns ISO 8601 ou AAAA-MM-DD
                data_emissao = datetime.fromisoformat(data_emissao_str.replace('Z', '+00:00'))
            except ValueError:
                try:
                    data_emissao = datetime.strptime(data_emissao_str, '%Y-%m-%d')
                except ValueError:
                    data_emissao = datetime.utcnow() # Fallback

            emitente_cnpj = self._find_text('.//nfe:emit/nfe:CNPJ')
            emitente_nome = self._find_text('.//nfe:emit/nfe:xNome')
            
            destinatario_cnpj = self._find_text('.//nfe:dest/nfe:CNPJ')
            if destinatario_cnpj == 'N/A': # Pode ser CPF
                destinatario_cnpj = self._find_text('.//nfe:dest/nfe:CPF')

            destinatario_nome = self._find_text('.//nfe:dest/nfe:xNome')

            # Validação básica de campos essenciais
            if not all([chave_acesso, numero, emitente_cnpj, destinatario_cnpj]):
                raise ValueError("Dados essenciais da NF-e ausentes ou inválidos.")

            return {
                'chave_acesso': chave_acesso,
                'numero': numero,
                'emitente_cnpj': emitente_cnpj,
                'emitente_nome': emitente_nome,
                'destinatario_cnpj': destinatario_cnpj,
                'destinatario_nome': destinatario_nome,
                'valor_total': valor_total,
                'data_emissao': data_emissao,
                'xml_filename': os.path.basename(self.xml_path)
            }
        except Exception as e:
            raise Exception(f"Erro ao parsear XML {self.xml_path}: {e}")

    def validate_signature(self):
        # SIMULAÇÃO: A validação real da assinatura digital é complexa e exige
        # bibliotecas como xmlsec ou ferramentas externas.
        # Para este protótipo, apenas retornamos True.
        print(f"Simulando validação de assinatura para {os.path.basename(self.xml_path)}: OK")
        return True