package com.exemplo.nfe.service;

import com.exemplo.nfe.model.NFe;
import com.exemplo.nfe.repository.NFeRepository;
// As dependências do iText foram comentadas no pom.xml, então estas importações
// podem causar erros de compilação se as classes não forem encontradas.
// Se você removeu as dependências do iText, comente ou remova as linhas abaixo
// relacionadas ao iText para que o projeto compile.
// Para este serviço, vamos mantê-las comentadas para permitir a compilação
// e você pode reativá-las quando o problema de rede for resolvido.
// import com.itextpdf.kernel.pdf.PdfDocument;
// import com.itextpdf.kernel.pdf.PdfWriter;
// import com.itextpdf.layout.Document;
// import com.itextpdf.layout.element.Paragraph;
// import com.itextpdf.layout.element.Table;
// import com.itextpdf.layout.properties.UnitValue;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.time.LocalDate;
import java.time.LocalDateTime; // Adicionado para compatibilidade com NFe.dataEmissao
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.stream.Collectors; // Importado para Collectors

/**
 * Serviço responsável pela lógica de negócios para geração de relatórios de NF-e.
 */
@Service
public class RelatorioService {

    @Autowired
    private NFeRepository nfeRepository;

    /**
     * Busca NF-e do repositório com base nos filtros fornecidos.
     * Em uma aplicação real, esta consulta seria mais complexa e otimizada.
     * Atualmente, busca todas e filtra em memória (para H2 em memória).
     * Para um banco de dados persistente, o repositório faria o filtro diretamente.
     * @param startDate Data de início do período.
     * @param endDate Data de fim do período.
     * @param fornecedor Nome do fornecedor.
     * @param status Status da NF-e.
     * @return Lista de NF-e que correspondem aos filtros.
     */
    public List<NFe> findNFeForReport(LocalDate startDate, LocalDate endDate, String fornecedor, String status) {
        // Usa o método do repositório se os parâmetros forem fornecidos
        // Note: o NFeRepository.findByDataEmissaoBetweenAndEmissorContainingIgnoreCaseAndStatusContainingIgnoreCase
        // espera LocalDateTime, então convertemos LocalDate para LocalDateTime.
        // Se a busca for complexa, considere usar Specification ou QueryDSL.

        // Se todos os filtros estão vazios, retorna todos os NFes
        if (startDate == null && endDate == null && (fornecedor == null || fornecedor.isEmpty()) && (status == null || status.isEmpty())) {
            return nfeRepository.findAll();
        }

        // Converte LocalDate para LocalDateTime para a consulta do repositório, se necessário
        LocalDateTime startDateTime = (startDate != null) ? startDate.atStartOfDay() : null;
        LocalDateTime endDateTime = (endDate != null) ? endDate.atTime(23, 59, 59) : null;

        // Recupera todos os NFes e aplica o filtro em memória,
        // pois o método de repositório exato para todos os filtros pode ser complexo
        // ou exigir índices específicos no banco de dados.
        // Em um cenário real, você otimizaria isso com @Query ou QueryDSL.
        List<NFe> allNfes = nfeRepository.findAll();

        return allNfes.stream()
                .filter(nfe -> {
                    boolean matches = true;

                    // Filtro por data de emissão
                    if (startDate != null && nfe.getDataEmissao() != null && nfe.getDataEmissao().isBefore(startDateTime)) {
                        matches = false;
                    }
                    if (endDate != null && nfe.getDataEmissao() != null && nfe.getDataEmissao().isAfter(endDateTime)) {
                        matches = false;
                    }

                    // Filtro por fornecedor (emissor)
                    if (fornecedor != null && !fornecedor.isEmpty()) {
                        if (nfe.getEmissor() == null || !nfe.getEmissor().toLowerCase().contains(fornecedor.toLowerCase())) {
                            matches = false;
                        }
                    }

                    // Filtro por status
                    if (status != null && !status.isEmpty()) {
                        if (nfe.getStatus() == null || !nfe.getStatus().equalsIgnoreCase(status)) {
                            matches = false;
                        }
                    }
                    return matches;
                })
                .collect(Collectors.toList());
    }

    /**
     * Gera um arquivo CSV a partir de uma lista de NF-e.
     * @param nfes Lista de NF-e a serem incluídas no CSV.
     * @return Array de bytes do arquivo CSV.
     * @throws IOException Se ocorrer um erro de I/O.
     */
    public byte[] generateCsv(List<NFe> nfes) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        PrintWriter writer = new PrintWriter(out);

        // Define o cabeçalho do CSV
        String[] headers = {"ID", "Chave", "Número", "Emissor", "CNPJ Emissor", "Data Emissão", "Valor", "Status", "Caminho XML"};
        CSVFormat csvFormat = CSVFormat.DEFAULT.builder()
                .setHeader(headers)
                .build();

        try (CSVPrinter csvPrinter = new CSVPrinter(writer, csvFormat)) {
            for (NFe nfe : nfes) {
                csvPrinter.printRecord(
                        nfe.getId(),
                        nfe.getChave(),
                        nfe.getNumero(),
                        nfe.getEmissor(),
                        nfe.getEmissorCnpj(),
                        nfe.getDataEmissao() != null ? nfe.getDataEmissao().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME) : "",
                        nfe.getValor(),
                        nfe.getStatus(),
                        nfe.getCaminhoXml()
                );
            }
            csvPrinter.flush();
        }

        return out.toByteArray();
    }

    /**
     * Gera um arquivo PDF a partir de uma lista de NF-e.
     * ATENÇÃO: Esta funcionalidade depende das bibliotecas iText, que foram
     * comentadas no pom.xml devido a problemas de conectividade.
     * Se você não tiver as dependências do iText, este método causará
     * erros de compilação ou de tempo de execução.
     * @param nfes Lista de NF-e a serem incluídas no PDF.
     * @return Array de bytes do arquivo PDF.
     * @throws IOException Se ocorrer um erro de I/O.
     */
    public byte[] generatePdf(List<NFe> nfes) throws IOException {
        // Implementação de geração de PDF comentada, pois as dependências do iText
        // foram removidas/comentadas no pom.xml.
        // Descomente e reative quando as dependências do iText puderem ser baixadas.

        /*
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        PdfWriter writer = new PdfWriter(out);
        PdfDocument pdf = new PdfDocument(writer);
        Document document = new Document(pdf);

        document.add(new Paragraph("Relatório de Notas Fiscais Eletrônicas"));
        document.add(new Paragraph("Gerado em: " + LocalDateTime.now().format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss"))));
        document.add(new Paragraph("\n")); // Espaço

        // Tabela para os dados das NF-e
        float[] columnWidths = {1, 3, 1, 2, 2, 2, 1, 1, 2}; // 9 colunas
        Table table = new Table(UnitValue.createPercentArray(columnWidths));
        table.setWidth(UnitValue.createPercentValue(100)); // 100% da largura

        // Cabeçalhos da tabela
        table.addHeaderCell("ID");
        table.addHeaderCell("Chave");
        table.addHeaderCell("Número");
        table.addHeaderCell("Emissor");
        table.addHeaderCell("CNPJ Emissor");
        table.addHeaderCell("Data Emissão");
        table.addHeaderCell("Valor");
        table.addHeaderCell("Status");
        table.addHeaderCell("Caminho XML");

        // Adiciona os dados das NF-e
        for (NFe nfe : nfes) {
            table.addCell(nfe.getId() != null ? nfe.getId().toString() : "");
            table.addCell(nfe.getChave() != null ? nfe.getChave() : "");
            table.addCell(nfe.getNumero() != null ? nfe.getNumero().toString() : "");
            table.addCell(nfe.getEmissor() != null ? nfe.getEmissor() : "");
            table.addCell(nfe.getEmissorCnpj() != null ? nfe.getEmissorCnpj() : "");
            table.addCell(nfe.getDataEmissao() != null ? nfe.getDataEmissao().format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm")) : "");
            table.addCell(nfe.getValor() != null ? nfe.getValor().toString() : "");
            table.addCell(nfe.getStatus() != null ? nfe.getStatus() : "");
            table.addCell(nfe.getCaminhoXml() != null ? nfe.getCaminhoXml() : "");
        }

        document.add(table);
        document.close();

        return out.toByteArray();
        */
        // Retorna um array de bytes vazio ou lança uma exceção para indicar que o PDF não pode ser gerado
        // já que as dependências estão ausentes.
        throw new UnsupportedOperationException("Geração de PDF não disponível: dependências iText ausentes.");
    }
}
