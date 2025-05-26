package com.exemplo.nfe.service;

import javax.xml.XMLConstants;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;
import javax.xml.transform.stream.StreamSource;
import java.io.File; // Importar java.io.File
import java.io.IOException; // Importar java.io.IOException
import java.net.URL; // Importar java.net.URL
import org.xml.sax.SAXException;


public class XMLValidatorService {

    public void validarXML(File xmlFile) throws SAXException, IOException {
        // 1. Criar uma fábrica de schemas XML
        SchemaFactory factory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);

        // 2. Carregar o arquivo XSD (schema)
        // O método getResource busca o arquivo no classpath.
        // Certifique-se de que o XSD esteja em src/main/resources/xsd/
        URL xsdPath = this.getClass().getClassLoader().getResource("xsd/NFe_v4.00.xsd");
        if (xsdPath == null) {
            throw new IOException("Arquivo XSD não encontrado no classpath: xsd/NFe_v4.00.xsd");
        }
        Schema schema = factory.newSchema(xsdPath);

        // 3. Criar um validador a partir do schema
        Validator validator = schema.newValidator();

        // 4. Validar o arquivo XML contra o schema
        // Se houver erros de validação, uma SAXException será lançada.
        validator.validate(new StreamSource(xmlFile));
        System.out.println("XML validado com sucesso contra o XSD.");
    }
}