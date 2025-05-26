package com.exemplo.nfe.repository;

import com.exemplo.nfe.model.Usuario;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UsuarioRepository extends JpaRepository<Usuario, Long> {
    /**
     * Busca um usuário pelo seu endereço de e-mail.
     * @param email O e-mail do usuário.
     * @return Um Optional contendo o usuário, se encontrado.
     */
    Optional<Usuario> findByEmail(String email);

    /**
     * Busca um usuário pelo seu nome de usuário (username).
     * @param username O nome de usuário.
     * @return Um Optional contendo o usuário, se encontrado.
     */
    Optional<Usuario> findByUsername(String username);
}
