package com.exemplo.nfe.controller;

import com.exemplo.nfe.model.NFe;
import com.exemplo.nfe.repository.NFeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.User;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.Principal;

@Controller
public class NFeController {

    @Autowired
    private NFeRepository nfeRepository;

    // ESTE MÉTODO ESTAVA CAUSANDO O ERRO DE MAPEAMENTO AMBÍGUO.
    // Ele foi removido ou comentado para resolver o conflito com WebController.
    // @GetMapping("/")
    // public String getMethodName(@RequestParam String param) {
    //     return new String();
    // }

    /**
     * Mapeia a URL "/dashboard" para a página do dashboard.
     * Exibe uma lista de NF-e e verifica se o usuário é administrador.
     *
     * @param model Objeto Model para adicionar atributos para a view.
     * @param principal Objeto Principal que representa o usuário autenticado.
     * @return O nome da view (template Thymeleaf) para a página do dashboard.
     */
    @GetMapping("/dashboard") // <--- Adicionado este mapeamento para o dashboard
    public String home(Model model, Principal principal) {
        // Busca todas as NF-e do repositório para exibir no dashboard
        model.addAttribute("nfes", nfeRepository.findAll());

        // Verifica se o usuário autenticado é administrador para controle de acesso na view
        if (principal != null) {
            // O principal pode ser um UserDetails, então fazemos um cast seguro
            Object principalObj = SecurityContextHolder.getContext().getAuthentication().getPrincipal();
            if (principalObj instanceof User) {
                User user = (User) principalObj;
                model.addAttribute("isAdmin", user.getAuthorities().stream()
                    .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN")));
            } else {
                model.addAttribute("isAdmin", false); // Não é um UserDetails, não é admin
            }
        } else {
            model.addAttribute("isAdmin", false); // Usuário não autenticado
        }

        return "dashboard"; // Retorna o template dashboard.html
    }

    /**
     * Lida com o upload de arquivos XML de NF-e.
     * Salva o arquivo no diretório "uploads" e registra uma nova NF-e no banco de dados.
     *
     * @param arquivo O arquivo MultipartFile enviado.
     * @return Um redirecionamento para a página do dashboard após o upload.
     * @throws IOException Se ocorrer um erro de I/O durante o salvamento do arquivo.
     */
    @PostMapping("/upload")
    public String upload(@RequestParam("arquivo") MultipartFile arquivo) throws IOException {
        // Define o caminho de destino para o arquivo uploaded
        Path destino = Paths.get("uploads/" + arquivo.getOriginalFilename());
        // Cria os diretórios necessários se não existirem
        Files.createDirectories(destino.getParent());
        // Escreve os bytes do arquivo no destino
        Files.write(destino, arquivo.getBytes());

        // Cria uma nova instância de NFe e preenche com dados simulados
        NFe nfe = new NFe();
        nfe.setChave("CHAVE_SIMULADA_" + System.currentTimeMillis()); // Chave simulada
        nfe.setCaminhoXml(destino.toString()); // Caminho do arquivo XML salvo
        // Você pode adicionar mais atributos da NFe aqui, se puder extraí-los do XML
        // nfe.setNumero(...);
        // nfe.setEmissor(...);
        // nfe.setValor(...);
        // nfe.setDataEmissao(LocalDateTime.now());
        // nfe.setStatus("PROCESSADA");

        // Salva a nova NFe no repositório
        nfeRepository.save(nfe);

        // Redireciona para o dashboard após o upload bem-sucedido
        return "redirect:/dashboard";
    }
}
