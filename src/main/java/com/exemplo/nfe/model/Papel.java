package com.exemplo.nfe.model;

import jakarta.persistence.*;
import java.util.Objects;
import java.util.Set;

import com.fasterxml.jackson.annotation.JsonIgnore;

@Entity
@Table(name = "papeis")
public class Papel {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Enumerated(EnumType.STRING) // Armazena o nome da enumeração como String no banco de dados
    @Column(length = 20, unique = true, nullable = false) // Garante que o nome do papel seja único
    private EPapel nome;

    @ManyToMany(mappedBy = "papeis")
    @JsonIgnore
    private Set<Usuario> usuarios; // Relacionamento Many-to-Many com Usuario

    // Construtor padrão
    public Papel() {}

    // Construtor com nome
    public Papel(EPapel nome) {
        this.nome = nome;
    }

    // Getters e Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public EPapel getNome() {
        return nome;
    }

    public void setNome(EPapel nome) {
        this.nome = nome;
    }

    public Set<Usuario> getUsuarios() {
        return usuarios;
    }

    public void setUsuarios(Set<Usuario> usuarios) {
        this.usuarios = usuarios;
    }

    @Override
    public String toString() {
        return "Papel{" +
               "id=" + id +
               ", nome=" + nome +
               '}';
    }
        @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Papel papel = (Papel) o;
        return id != null && Objects.equals(id, papel.id);
    }

    @Override
    public int hashCode() {
        return id == null ? 0 : Objects.hash(id);
    }
}
