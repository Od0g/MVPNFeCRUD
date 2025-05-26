package com.exemplo.nfe.repository;

import com.exemplo.nfe.model.AuditoriaLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface AuditoriaRepository extends JpaRepository<AuditoriaLog, Long> {
    // Métodos de consulta personalizados podem ser adicionados aqui, se necessário
}
