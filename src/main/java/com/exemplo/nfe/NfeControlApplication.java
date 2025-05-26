package com.exemplo.nfe;

import com.exemplo.nfe.model.EPapel;
import com.exemplo.nfe.model.Papel;
import com.exemplo.nfe.model.Usuario;
import com.exemplo.nfe.repository.PapelRepository;
import com.exemplo.nfe.repository.UsuarioRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.client.RestTemplate; // Adicionado: Importar RestTemplate

import java.util.HashSet;
import java.util.Optional;
import java.util.Set;

/**
 * Classe principal da aplicação Spring Boot para o NFe Control.
 * Esta classe é o ponto de entrada da aplicação.
 *
 * Anotações:
 * - @SpringBootApplication: Combina @Configuration, @EnableAutoConfiguration e @ComponentScan.
 * - @EnableScheduling: Habilita o agendamento de tarefas no Spring (necessário para o BackupService).
 */
@SpringBootApplication
@EnableScheduling
public class NfeControlApplication {

    /**
     * Método principal que inicia a aplicação Spring Boot.
     *
     * @param args Argumentos da linha de comando.
     */
    public static void main(String[] args) {
        SpringApplication.run(NfeControlApplication.class, args);
    }

    /**
     * Bean CommandLineRunner para inicializar dados no startup da aplicação.
     * Neste caso, cria um usuário administrador se ele ainda não existir.
     *
     * @param usuarioRepo Repositório para a entidade Usuario.
     * @param papelRepo Repositório para a entidade Papel.
     * @param encoder Codificador de senhas do Spring Security.
     * @return Uma instância de CommandLineRunner.
     */
    @Bean
    public CommandLineRunner init(UsuarioRepository usuarioRepo, PapelRepository papelRepo, PasswordEncoder encoder) {
        return args -> {
            // Verifica se o papel ADMIN já existe, se não, cria
            Optional<Papel> adminRole = papelRepo.findByNome(EPapel.ADMIN);
            Papel papelAdmin;
            if (adminRole.isEmpty()) {
                papelAdmin = new Papel();
                papelAdmin.setNome(EPapel.ADMIN);
                papelAdmin = papelRepo.save(papelAdmin);
            } else {
                papelAdmin = adminRole.get();
            }

            // Verifica se o usuário admin@teste.com já existe
            if (usuarioRepo.findByEmail("admin@teste.com").isEmpty()) {
                Usuario admin = new Usuario();
                admin.setEmail("admin@teste.com");
                admin.setUsername("admin"); // Adicionado username para consistência com CustomUserDetailsService
                admin.setSenha(encoder.encode("123")); // Senha criptografada
                admin.setEnabled(true); // Usuário ativo

                Set<Papel> papeis = new HashSet<>();
                papeis.add(papelAdmin);
                admin.setPapeis(papeis); // Associa o papel ADMIN ao usuário

                usuarioRepo.save(admin);
                System.out.println("Usuário administrador 'admin@teste.com' criado com sucesso!");
            } else {
                System.out.println("Usuário administrador 'admin@teste.com' já existe.");
            }
        };
    }

    /**
     * Define um bean para RestTemplate.
     * RestTemplate é uma classe síncrona para realizar requisições HTTP.
     * É injetado automaticamente em serviços que o requerem (como IntegracaoSefazService).
     * @return Uma nova instância de RestTemplate.
     */
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
