package com.exemplo.nfe.model;

import jakarta.persistence.Column; // Adicionado: Importar jakarta.persistence.Column
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.LocalDateTime;

@Entity
@Table(name = "auditoria_logs")
public class AuditoriaLog {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String usuario; // Usuário que realizou a ação
    private String acao;    // Nome do método ou tipo de ação
    private LocalDateTime dataHora; // Timestamp da ação
    @Column(length = 1000) // Aumenta o tamanho da coluna para detalhes mais longos
    private String detalhes; // Detalhes adicionais da ação (ex: parâmetros, resultado)

    // Construtor padrão
    public AuditoriaLog() {}

    // Getters e Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getUsuario() { return usuario; }
    public void setUsuario(String usuario) { this.usuario = usuario; }
    public String getAcao() { return acao; }
    public void setAcao(String acao) { this.acao = acao; }
    public LocalDateTime getDataHora() { return dataHora; }
    public void setDataHora(LocalDateTime dataHora) { this.dataHora = dataHora; }
    public String getDetalhes() { return detalhes; }
    public void setDetalhes(String detalhes) { this.detalhes = detalhes; }

    @Override
    public String toString() {
        return "AuditoriaLog{" +
               "id=" + id +
               ", usuario='" + usuario + '\'' +
               ", acao='" + acao + '\'' +
               ", dataHora=" + dataHora +
               ", detalhes='" + detalhes + '\'' +
               '}';
    }
}
