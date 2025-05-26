package com.exemplo.nfe.service;

import com.exemplo.nfe.model.Usuario;
import com.exemplo.nfe.repository.UsuarioRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.Collection;
import java.util.stream.Collectors;

@Service
public class CustomUserDetailsService implements UserDetailsService {

    @Autowired
    private UsuarioRepository usuarioRepository;

    /**
     * Carrega os detalhes do usuário pelo nome de usuário (username).
     *
     * @param username O nome de usuário (ou email, se configurado para isso).
     * @return Um objeto UserDetails contendo os detalhes do usuário e suas autoridades.
     * @throws UsernameNotFoundException Se o usuário não for encontrado.
     */
    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        // Tentativa de buscar por username (para login)
        Usuario usuario = usuarioRepository.findByUsername(username)
            .orElseGet(() -> usuarioRepository.findByEmail(username) // Tenta buscar por email se não encontrar por username
                .orElseThrow(() -> new UsernameNotFoundException("Usuário não encontrado: " + username)));

        // Converte os papéis e permissões do seu modelo para GrantedAuthority do Spring Security
        Collection<? extends GrantedAuthority> authorities =
            usuario.getPapeis().stream()
                .map(papel -> new SimpleGrantedAuthority("ROLE_" + papel.getNome().name())) // Adiciona prefixo ROLE_ para papéis
                .collect(Collectors.toSet());

        // Adiciona permissões granulares (se houver)
        // Se você tiver um relacionamento direto de Permissao com Usuario, adicione aqui
        // Exemplo: usuario.getPermissoes().stream().map(p -> new SimpleGrantedAuthority(p.getNome())).forEach(authorities::add);

        return new org.springframework.security.core.userdetails.User(
            usuario.getUsername(), // Ou email, dependendo de como você quer que o Spring Security identifique o usuário
            usuario.getSenha(), // Corrigido: Usar getSenha() em vez de getPassword()
            usuario.isEnabled(), // enabled
            true, // accountNonExpired
            true, // credentialsNonExpired
            true, // accountNonLocked
            authorities
        );
    }
}
