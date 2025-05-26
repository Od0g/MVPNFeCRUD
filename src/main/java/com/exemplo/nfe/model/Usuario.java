package com.exemplo.nfe.model;

import com.fasterxml.jackson.annotation.JsonIgnore; // Importar esta anotação
import jakarta.persistence.*;
import java.util.Objects;
import java.util.HashSet;
import java.util.Set;



@Entity
@Table(name = "usuarios")
public class Usuario {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String username;
    @Column(unique = true, nullable = false)
    private String email;
    @Column(nullable = false)
    private String senha; // Renomeado de 'password' para 'senha'
    private boolean enabled = true; // Se o usuário está ativo

    // Relacionamento Many-to-Many com Papel
    @ManyToMany(fetch = FetchType.EAGER) // Carrega os papéis junto com o usuário
    
    @JoinTable(
        name = "usuario_papel",
        joinColumns = @JoinColumn(name = "usuario_id"),
        inverseJoinColumns = @JoinColumn(name = "papel_id")
    )
    @JsonIgnore // ADd
    private Set<Papel> papeis = new HashSet<>();

    // Relacionamento Many-to-Many com Permissao (se usar permissões granulares separadas dos papéis)
    @ManyToMany(fetch = FetchType.EAGER)
    @JoinTable(
        name = "usuario_permissao",
        joinColumns = @JoinColumn(name = "usuario_id"),
        inverseJoinColumns = @JoinColumn(name = "permissao_id")
    )
    @JsonIgnore // ADICIONE ESTA LINHA
    private Set<Permissao> permissoes = new HashSet<>();

    // Construtor padrão
    public Usuario() {}

    // Getters e Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getSenha() { return senha; }
    public void setSenha(String senha) { this.senha = senha; }
    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }
    public Set<Papel> getPapeis() { return papeis; }
    public void setPapeis(Set<Papel> papeis) { this.papeis = papeis; }
    public Set<Permissao> getPermissoes() { return permissoes; }
    public void setPermissoes(Set<Permissao> permissoes) { this.permissoes = permissoes; }

    @Override
    public String toString() {
        return "Usuario{" +
               "id=" + id +
               ", username='" + username + '\'' +
               ", email='" + email + '\'' +
               ", enabled=" + enabled +
               //", papeis=" + papeis.stream().map(Papel::getNome).collect(Collectors.toSet()) +
               //", permissoes=" + permissoes.stream().map(Permissao::getNome).collect(Collectors.toSet()) +
               '}';
    }
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        // Usa 'getClass()' para comparar classes (seguro com proxies do Hibernate)
        if (o == null || getClass() != o.getClass()) return false;
        Usuario usuario = (Usuario) o;
        // Compara apenas pelo ID. Se o ID ainda é nulo (entidade nova),
        // eles são iguais apenas se forem a mesma instância.
        return id != null && Objects.equals(id, usuario.id);
    }

    @Override
    public int hashCode() {
        // Gera o hashCode baseado apenas no ID.
        // Se o ID for nulo (entidade nova), retorna um valor constante
        // para evitar problemas em coleções antes de o ID ser gerado.
        return id == null ? 0 : Objects.hash(id);
    }
}
