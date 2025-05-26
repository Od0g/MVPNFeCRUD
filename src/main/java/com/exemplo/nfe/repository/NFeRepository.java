package com.exemplo.nfe.repository;

import com.exemplo.nfe.model.NFe;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface NFeRepository extends JpaRepository<NFe, Long> {
    Optional<NFe> findByChave(String chave);
    boolean existsByChave(String chave);

    // Novo método para buscar NF-e com filtros para relatórios
    // Spring Data JPA pode criar a query automaticamente se o nome do método seguir o padrão
    List<NFe> findByDataEmissaoBetweenAndEmissorContainingIgnoreCaseAndStatusContainingIgnoreCase(
            LocalDateTime startDate, LocalDateTime endDate, String emissor, String status);

    // Você também pode adicionar métodos para buscar por fornecedor (emitente) e status
    List<NFe> findByEmissorContainingIgnoreCase(String emissor);
    List<NFe> findByStatusIgnoreCase(String status);
    List<NFe> findByDataEmissaoBetween(LocalDateTime startDate, LocalDateTime endDate);

    // Exemplo de Query personalizada para filtros mais complexos (se necessário)
    /*
    @Query("SELECT n FROM NFe n WHERE " +
           "(:startDate IS NULL OR n.dataEmissao >= :startDate) AND " +
           "(:endDate IS NULL OR n.dataEmissao <= :endDate) AND " +
           "(:fornecedor IS NULL OR LOWER(n.emissor) LIKE LOWER(CONCAT('%', :fornecedor, '%'))) AND " +
           "(:status IS NULL OR LOWER(n.status) LIKE LOWER(CONCAT('%', :status, '%')))")
    List<NFe> findNFeByCriteria(@Param("startDate") LocalDateTime startDate,
                                @Param("endDate") LocalDateTime endDate,
                                @Param("fornecedor") String fornecedor,
                                @Param("status") String status);
    */
}
