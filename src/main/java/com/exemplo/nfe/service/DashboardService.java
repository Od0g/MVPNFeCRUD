package com.exemplo.nfe.service;

import com.exemplo.nfe.repository.NFeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.Month;
import java.time.format.TextStyle;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class DashboardService {

    @Autowired
    private NFeRepository nfeRepository;

    /**
     * Retorna a contagem de NF-e por status.
     * Em uma aplicação real, isso faria uma consulta agregada ao banco de dados.
     * Atualmente, retorna dados mockados.
     * @return Um mapa com labels (status) e values (contagens).
     */
    public Map<String, List<?>> getNFeStatusCounts() {
        // Exemplo de dados mockados. Em produção, você faria uma consulta como:
        // List<Object[]> results = nfeRepository.countNFeByStatus();
        // data.put("labels", results.stream().map(r -> (String) r[0]).collect(Collectors.toList()));
        // data.put("values", results.stream().map(r -> (Long) r[1]).collect(Collectors.toList()));

        Map<String, List<?>> data = new HashMap<>();
        data.put("labels", Arrays.asList("Autorizada", "Cancelada", "Denegada", "Rejeitada"));
        data.put("values", Arrays.asList(150, 20, 5, 10));
        return data;
    }

    /**
     * Retorna a movimentação mensal de NF-e.
     * Em uma aplicação real, isso faria uma consulta agregada ao banco de dados.
     * Atualmente, retorna dados mockados.
     * @return Um mapa com labels (meses) e values (contagens).
     */
    public Map<String, List<?>> getNFeMonthlyMovement() {
        // Exemplo de dados mockados. Em produção, você faria uma consulta como:
        // List<Object[]> results = nfeRepository.countNFeMonthly();
        // data.put("labels", results.stream().map(r -> Month.of((Integer) r[0]).getDisplayName(TextStyle.SHORT, Locale.getDefault())).collect(Collectors.toList()));
        // data.put("values", results.stream().map(r -> (Long) r[1]).collect(Collectors.toList()));

        Map<String, List<?>> data = new HashMap<>();
        data.put("labels", Arrays.asList(
            Month.JANUARY.getDisplayName(TextStyle.SHORT, Locale.getDefault()),
            Month.FEBRUARY.getDisplayName(TextStyle.SHORT, Locale.getDefault()),
            Month.MARCH.getDisplayName(TextStyle.SHORT, Locale.getDefault()),
            Month.APRIL.getDisplayName(TextStyle.SHORT, Locale.getDefault()),
            Month.MAY.getDisplayName(TextStyle.SHORT, Locale.getDefault())
        ));
        data.put("values", Arrays.asList(120, 150, 130, 180, 165));
        return data;
    }
}
