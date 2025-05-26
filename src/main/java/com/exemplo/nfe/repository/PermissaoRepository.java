package com.exemplo.nfe.repository;

import com.exemplo.nfe.model.Permissao;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PermissaoRepository extends JpaRepository<Permissao, Long> {
    /**
     * Busca uma Permissão pelo seu nome.
     * @param nome O nome da permissão (ex: "RELATORIOS_GERAR").
     * @return Um Optional contendo a Permissão, se encontrada.
     */
    Optional<Permissao> findByNome(String nome);
}
