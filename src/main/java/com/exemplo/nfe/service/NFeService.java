package com.exemplo.nfe.service;

import com.exemplo.nfe.annotation.Auditoria;
import com.exemplo.nfe.model.AuditoriaLog; // Importar AuditoriaLog
import com.exemplo.nfe.model.NFe;
import com.exemplo.nfe.repository.AuditoriaRepository; // Importar AuditoriaRepository
import com.exemplo.nfe.repository.NFeRepository;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional; // Adicionado: Importar Optional
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class NFeService {

    private final NFeRepository nfeRepository; // Renomeado para clareza
    private final AuditoriaRepository auditoriaRepository; // Injetar AuditoriaRepository

    public NFeService(NFeRepository nfeRepository, AuditoriaRepository auditoriaRepository) {
        this.nfeRepository = nfeRepository;
        this.auditoriaRepository = auditoriaRepository;
    }

    /**
     * Consulta uma NF-e pela chave de acesso.
     *
     * @param chave Chave de acesso da NF-e.
     * @param usuario Nome do usuário que está realizando a consulta.
     * @return A NF-e encontrada ou uma nova instância se não encontrada.
     */
    public NFe consultarPorChave(String chave, String usuario) {
        // Implementação simplificada: buscar no repositório
        // Em uma aplicação real, você buscaria no banco de dados ou em um serviço externo.
        Optional<NFe> nfeOptional = nfeRepository.findByChave(chave);
        if (nfeOptional.isPresent()) {
            registrarHistorico(chave, usuario, "CONSULTA_NFE", true, null);
            return nfeOptional.get();
        } else {
            registrarHistorico(chave, usuario, "CONSULTA_NFE", false, "NFe não encontrada");
            NFe nfe = new NFe();
            nfe.setChave(chave);
            nfe.setStatus("NÃO ENCONTRADA");
            return nfe;
        }
    }

    /**
     * Registra um evento de auditoria.
     *
     * @param parametro Parâmetro principal da ação (ex: chave da NF-e).
     * @param usuario Nome do usuário que realizou a ação.
     * @param tipo Tipo da ação (ex: "CONSULTA_NFE", "CRIACAO_NFE").
     * @param sucesso Indica se a operação foi bem-sucedida.
     * @param mensagemErro Mensagem de erro, se houver.
     */
    private void registrarHistorico(String parametro, String usuario, String tipo,
                                    boolean sucesso, String mensagemErro) {
        AuditoriaLog log = new AuditoriaLog();
        log.setUsuario(usuario);
        log.setAcao(tipo);
        log.setDataHora(LocalDateTime.now());
        log.setDetalhes("Parâmetro: " + parametro + ", Sucesso: " + sucesso +
                        (mensagemErro != null ? ", Erro: " + mensagemErro : ""));
        auditoriaRepository.save(log);
        System.out.println("Histórico de auditoria registrado: " + log.getAcao() + " por " + log.getUsuario());
    }

    /**
     * Cria uma nova NF-e.
     *
     * @param novaNFe Objeto NFe a ser criado.
     * @return A NF-e criada.
     */
    @Auditoria(descricao = "Criação de nova NF-e")
    public NFe criarNFe(NFe novaNFe) {
        // Lógica para criar NF-e: salvar no banco de dados
        novaNFe.setDataEmissao(LocalDateTime.now());
        novaNFe.setStatus("AUTORIZADA"); // Status inicial
        nfeRepository.save(novaNFe);
        System.out.println("NF-e criada: " + novaNFe.getChave());
        return novaNFe;
    }

    /**
     * Atualiza uma NF-e existente.
     *
     * @param id ID da NF-e a ser atualizada.
     * @param nfeAtualizada Objeto NFe com os dados atualizados.
     * @return A NF-e atualizada.
     */
    @Auditoria(descricao = "Atualização de NF-e")
    public NFe atualizarNFe(Long id, NFe nfeAtualizada) {
        // Lógica para atualizar NF-e: buscar, atualizar e salvar
        return nfeRepository.findById(id).map(nfe -> {
            nfe.setChave(nfeAtualizada.getChave());
            nfe.setNumero(nfeAtualizada.getNumero());
            nfe.setEmissor(nfeAtualizada.getEmissor());
            nfe.setValor(nfeAtualizada.getValor());
            nfe.setStatus(nfeAtualizada.getStatus());
            // Outros campos a serem atualizados
            nfeRepository.save(nfe);
            System.out.println("NF-e atualizada: " + id);
            return nfe;
        }).orElseThrow(() -> new RuntimeException("NF-e não encontrada com ID: " + id));
    }

    /**
     * Busca uma NF-e pelo ID.
     * Este método não será auditado, pois não tem a anotação @Auditoria.
     *
     * @param id ID da NF-e.
     * @return A NF-e encontrada ou null.
     */
    public NFe buscarNFePorId(Long id) {
        return nfeRepository.findById(id).orElse(null);
    }

    /**
     * Busca todas as NF-e.
     *
     * @return Lista de todas as NF-e.
     */
    public List<NFe> buscarTodasNFe() {
        return nfeRepository.findAll();
    }

    /**
     * Filtra NF-e com base em data de início, data de fim e CNPJ do emitente.
     *
     * @param dataInicio Data de início para o filtro.
     * @param dataFim Data de fim para o filtro.
     * @param cnpjEmitente CNPJ do emitente para o filtro.
     * @return Lista de NF-e filtradas.
     */
    public List<NFe> filtrarNFe(LocalDate dataInicio, LocalDate dataFim, String cnpjEmitente) {
        List<NFe> allNfes = nfeRepository.findAll(); // Exemplo: buscar todas e filtrar em memória
        return allNfes.stream()
            .filter(nfe -> {
                boolean matchesDate = true;
                if (dataInicio != null && nfe.getDataEmissao() != null && nfe.getDataEmissao().toLocalDate().isBefore(dataInicio)) {
                    matchesDate = false;
                }
                if (dataFim != null && nfe.getDataEmissao() != null && nfe.getDataEmissao().toLocalDate().isAfter(dataFim)) {
                    matchesDate = false;
                }
                boolean matchesCnpj = true;
                if (cnpjEmitente != null && !cnpjEmitente.isEmpty() && (nfe.getEmissorCnpj() == null || !nfe.getEmissorCnpj().equals(cnpjEmitente))) {
                    matchesCnpj = false;
                }
                return matchesDate && matchesCnpj;
            })
            .collect(Collectors.toList());
    }

    /**
     * Valida a chave da NF-e (exemplo simplificado).
     * Em uma implementação real, envolveria validação de formato e dígito verificador.
     *
     * @param chave A chave da NF-e a ser validada.
     * @return true se a chave for válida, false caso contrário.
     */
    public boolean validarChaveNFe(String chave) {
        // Exemplo simplificado: verifica se tem 44 dígitos e é numérica
        return chave != null && chave.matches("\\d{44}");
    }
}
