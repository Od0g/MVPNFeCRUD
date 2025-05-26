package com.exemplo.nfe.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.security.access.prepost.PreAuthorize;

/**
 * Controlador responsável por servir as páginas HTML da aplicação.
 * Este controlador lida com redirecionamentos e páginas de acesso geral.
 */
@Controller
public class WebController {

    /**
     * Mapeia a URL raiz ("/") para a página de login.
     * Quando um usuário acessa a raiz, ele será redirecionado para o endpoint /login.
     * @return Um redirecionamento para o endpoint /login.
     */
    @GetMapping("/")
    public String redirectToLogin() {
        return "redirect:/login"; // Redireciona para o endpoint /login
    }

    /**
     * Mapeia a URL "/login" para a página de login.
     * @return O nome da view (template Thymeleaf) para a página de login.
     */
    @GetMapping("/login")
    public String login() {
        return "login"; // Retorna o template login.html
    }

    // O método dashboard() foi removido daqui para evitar conflito de mapeamento
    // com o NFeController, que agora é o responsável por /dashboard.
    // @GetMapping("/dashboard")
    // public String dashboard() {
    //     return "dashboard"; // Retorna o template dashboard.html
    // }

    /**
     * Mapeia a URL "/upload" para a página de upload de NF-e.
     * @return O nome da view (template Thymeleaf) para a página de upload.
     */
    @GetMapping("/upload")
    @PreAuthorize("hasAnyRole('ADMIN', 'OPERACIONAL')") // Apenas usuários com ADMIN ou OPERACIONAL
    public String uploadPage() {
        return "upload"; // Retorna o template upload.html
    }

    /**
     * Mapeia a URL "/detalhes-nfe" para a página de detalhes de uma NF-e.
     * Esta página provavelmente receberá um ID de NF-e para exibir os detalhes.
     * @return O nome da view (template Thymeleaf) para a página de detalhes da NF-e.
     */
    @GetMapping("/detalhes-nfe")
    @PreAuthorize("isAuthenticated()") // Apenas usuários autenticados
    public String detalhesNFePage() {
        return "detalhes-nfe"; // Retorna o template detalhes-nfe.html
    }

    /**
     * Mapeia a URL "/admin/usuarios" para a página de gerenciamento de usuários.
     * Esta página é protegida e só será acessível por usuários com papel ADMIN.
     * @return O nome da view (template Thymeleaf) para a página de gerenciamento de usuários.
     */
    @PreAuthorize("hasRole('ADMIN')") // Protege esta página para apenas administradores
    @GetMapping("/admin/usuarios")
    public String adminUsuariosPage() {
        return "admin/usuarios"; // Retorna o template admin/usuarios.html
    }

    /**
     * Mapeia a URL "/relatorios" para a página de relatórios.
     * Esta página será acessível por usuários com papel ADMIN ou RELATORIOS_GERAR.
     * @return O nome da view (template Thymeleaf) para a página de relatórios.
     */
    @PreAuthorize("hasAnyRole('ADMIN', 'RELATORIOS_GERAR')") // Protege esta página para administradores ou quem pode gerar relatórios
    @GetMapping("/relatorios")
    public String relatoriosPage() {
        return "relatorios"; // Retorna o template relatorios.html
    }
}
