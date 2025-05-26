package com.exemplo.nfe.model;

import java.util.Objects;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.ManyToMany;
import jakarta.persistence.Table;
import java.util.Set;

import com.fasterxml.jackson.annotation.JsonIgnore;

@Entity
@Table(name = "permissoes") // Nome da tabela para evitar conflito com 'papeis'
public class Permissao {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String nome; // Ex: "RELATORIOS_GERAR", "NFE_EXPORTAR"

    @ManyToMany(mappedBy = "permissoes") // Mapeado pelo campo 'permissoes' em Usuario
    @JsonIgnore
    private Set<Usuario> usuarios;

    // Getters e Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getNome() { return nome; }
    public void setNome(String nome) { this.nome = nome; }
    public Set<Usuario> getUsuarios() { return usuarios; }
    public void setUsuarios(Set<Usuario> usuarios) { this.usuarios = usuarios; }

    @Override
    public String toString() {
        return "Permissao{" +
               "id=" + id +
               ", nome='" + nome + '\'' +
               '}';
    }

        @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Permissao permissao = (Permissao) o;
        return id != null && Objects.equals(id, permissao.id);
    }

    @Override
    public int hashCode() {
        return id == null ? 0 : Objects.hash(id);
    }
}
