package com.exemplo.nfe.repository;

import com.exemplo.nfe.model.EPapel;
import com.exemplo.nfe.model.Papel;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PapelRepository extends JpaRepository<Papel, Long> {
    /**
     * Busca um Papel pelo seu nome (enumeração).
     * @param nome O nome do papel (ex: EPapel.ADMIN).
     * @return Um Optional contendo o Papel, se encontrado.
     */
    Optional<Papel> findByNome(EPapel nome);
}
