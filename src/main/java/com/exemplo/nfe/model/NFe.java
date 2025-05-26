package com.exemplo.nfe.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "nfes")
public class NFe {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(unique = true, nullable = false, length = 44)
    private String chave; // Chave de acesso da NF-e
    private Long numero;
    private String emissor; // Nome do emitente
    private String emissorCnpj; // CNPJ do emitente (adicionado para filtro)
    private BigDecimal valor;
    private LocalDateTime dataEmissao;
    private String status; // Ex: AUTORIZADA, CANCELADA, DENEGADA
    private String caminhoXml; // Adicionado: Caminho do arquivo XML no sistema de arquivos

    // Construtor padrão
    public NFe() {}

    // Getters e Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getChave() { return chave; }
    public void setChave(String chave) { this.chave = chave; }
    public Long getNumero() { return numero; }
    public void setNumero(Long numero) { this.numero = numero; }
    public String getEmissor() { return emissor; }
    public void setEmissor(String emissor) { this.emissor = emissor; }
    public String getEmissorCnpj() { return emissorCnpj; }
    public void setEmissorCnpj(String emissorCnpj) { this.emissorCnpj = emissorCnpj; }
    public BigDecimal getValor() { return valor; }
    public void setValor(BigDecimal valor) { this.valor = valor; }
    public LocalDateTime getDataEmissao() { return dataEmissao; }
    public void setDataEmissao(LocalDateTime dataEmissao) { this.dataEmissao = dataEmissao; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getCaminhoXml() { return caminhoXml; } // Getter para caminhoXml
    public void setCaminhoXml(String caminhoXml) { this.caminhoXml = caminhoXml; } // Setter para caminhoXml

    @Override
    public String toString() {
        return "NFe{" +
               "id=" + id +
               ", chave='" + chave + '\'' +
               ", numero=" + numero +
               ", emissor='" + emissor + '\'' +
               ", emissorCnpj='" + emissorCnpj + '\'' +
               ", valor=" + valor +
               ", dataEmissao=" + dataEmissao +
               ", status='" + status + '\'' +
               ", caminhoXml='" + caminhoXml + '\'' +
               '}';
    }
}
