package com.exemplo.nfe.controller;

import com.exemplo.nfe.model.NFe;
import com.exemplo.nfe.service.RelatorioService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

/**
 * Controlador REST para geração de relatórios de NF-e.
 * Acesso restrito a usuários com papel 'ADMIN' ou 'RELATORIOS_GERAR'.
 */
@RestController
@RequestMapping("/api/relatorios/nfe")
@PreAuthorize("hasAnyRole('ADMIN', 'RELATORIOS_GERAR')") // Protege todos os métodos deste controlador
@Tag(name = "Relatórios de NF-e", description = "APIs para gerar relatórios de NF-e em diferentes formatos")
public class RelatorioController {

    @Autowired
    private RelatorioService relatorioService;

    /**
     * Gera um relatório de NF-e em formato CSV com base nos filtros fornecidos.
     * @param startDate Data de início do período (opcional).
     * @param endDate Data de fim do período (opcional).
     * @param fornecedor Nome do fornecedor (opcional).
     * @param status Status da NF-e (opcional, ex: "RECEBIDA", "EXPEDIDA").
     * @return ResponseEntity contendo o arquivo CSV.
     */
    @Operation(summary = "Gerar relatório de NF-e em CSV")
    @GetMapping(value = "/csv", produces = "text/csv")
    public ResponseEntity<byte[]> generateCsvReport(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate,
            @RequestParam(required = false) String fornecedor,
            @RequestParam(required = false) String status) {
        try {
            List<NFe> nfes = relatorioService.findNFeForReport(startDate, endDate, fornecedor, status);
            byte[] csvBytes = relatorioService.generateCsv(nfes);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.parseMediaType("text/csv"));
            headers.setContentDispositionFormData("attachment", "relatorio_nfes.csv");
            return new ResponseEntity<>(csvBytes, headers, HttpStatus.OK);
        } catch (Exception e) {
            // Logar o erro para depuração
            System.err.println("Erro ao gerar relatório CSV: " + e.getMessage());
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    /**
     * Gera um relatório de NF-e em formato PDF com base nos filtros fornecidos.
     * @param startDate Data de início do período (opcional).
     * @param endDate Data de fim do período (opcional).
     * @param fornecedor Nome do fornecedor (opcional).
     * @param status Status da NF-e (opcional, ex: "RECEBIDA", "EXPEDIDA").
     * @return ResponseEntity contendo o arquivo PDF.
     */
    @Operation(summary = "Gerar relatório de NF-e em PDF")
    @GetMapping(value = "/pdf", produces = "application/pdf")
    public ResponseEntity<byte[]> generatePdfReport(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate,
            @RequestParam(required = false) String fornecedor,
            @RequestParam(required = false) String status) {
        try {
            List<NFe> nfes = relatorioService.findNFeForReport(startDate, endDate, fornecedor, status);
            byte[] pdfBytes = relatorioService.generatePdf(nfes);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.parseMediaType("application/pdf"));
            headers.setContentDispositionFormData("attachment", "relatorio_nfes.pdf");
            return new ResponseEntity<>(pdfBytes, headers, HttpStatus.OK);
        } catch (Exception e) {
            // Logar o erro para depuração
            System.err.println("Erro ao gerar relatório PDF: " + e.getMessage());
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
}
