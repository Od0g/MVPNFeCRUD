package com.exemplo.nfe.controller;

import com.exemplo.nfe.service.DashboardService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/dashboard")
@Tag(name = "Dashboard", description = "API para dados do dashboard operacional")
public class DashboardController {

    @Autowired
    private DashboardService dashboardService;

    @Operation(summary = "Obter dados de status de NF-e para o dashboard")
    @GetMapping("/statusNFe")
    @PreAuthorize("isAuthenticated()") // Apenas usuários autenticados podem acessar
    public ResponseEntity<Map<String, List<?>>> getStatusNFeData() {
        Map<String, List<?>> data = dashboardService.getNFeStatusCounts();
        return ResponseEntity.ok(data);
    }

    @Operation(summary = "Obter dados de movimentação mensal de NF-e para o dashboard")
    @GetMapping("/movimentacaoMensal")
    @PreAuthorize("isAuthenticated()") // Apenas usuários autenticados podem acessar
    public ResponseEntity<Map<String, List<?>>> getMovimentacaoMensalData() {
        Map<String, List<?>> data = dashboardService.getNFeMonthlyMovement();
        return ResponseEntity.ok(data);
    }
}
