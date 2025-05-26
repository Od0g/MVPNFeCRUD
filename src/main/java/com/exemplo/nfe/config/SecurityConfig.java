package com.exemplo.nfe.config;

import com.exemplo.nfe.service.CustomUserDetailsService;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.util.matcher.AntPathRequestMatcher;

import static org.springframework.security.config.Customizer.withDefaults;

@Configuration
@EnableWebSecurity // Habilita a segurança web do Spring
@EnableMethodSecurity // Habilita segurança baseada em anotações (ex: @PreAuthorize)
public class SecurityConfig {

    /**
     * Define o codificador de senhas (BCryptPasswordEncoder) que será usado na aplicação.
     * Essencial para armazenar senhas de forma segura.
     * @return Uma instância de PasswordEncoder.
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    /**
     * Define o UserDetailsService personalizado e o PasswordEncoder para o provedor de autenticação.
     * @param customUserDetailsService O serviço que carrega os detalhes do usuário.
     * @param passwordEncoder O codificador de senhas.
     * @return Um AuthenticationProvider configurado.
     */
    @Bean
    public AuthenticationProvider authenticationProvider(CustomUserDetailsService customUserDetailsService, PasswordEncoder passwordEncoder) {
        DaoAuthenticationProvider authenticationProvider = new DaoAuthenticationProvider();
        authenticationProvider.setUserDetailsService(customUserDetailsService);
        authenticationProvider.setPasswordEncoder(passwordEncoder);
        return authenticationProvider;
    }

    /**
     * Configura a cadeia de filtros de segurança HTTP.
     * Define regras de autorização para diferentes URLs e configura formulário de login e logout.
     * @param http O objeto HttpSecurity para configurar a segurança.
     * @return Uma SecurityFilterChain configurada.
     * @throws Exception Se ocorrer um erro na configuração.
     */
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable) // Desabilita CSRF para APIs REST (considere habilitar para apps web com formulários)
            .authorizeHttpRequests(auth -> auth
                // Permite acesso público a certas URLs
                .requestMatchers(
                    "/login",
                    "/error",
                    "/webjars/**",
                    "/swagger-ui/**",
                    "/v3/api-docs/**",
                    "/api/public/**" // Ex: endpoints públicos
                ).permitAll()
                // Requer papel ADMIN para URLs de administração
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                // Requer permissão específica ou papel ADMIN para relatórios
                .requestMatchers("/api/relatorios/**").hasAnyAuthority("RELATORIOS_GERAR", "ROLE_ADMIN")
                // Requer permissão específica ou papel ADMIN para exportação de NF-e
                .requestMatchers("/api/nfe/exportar").hasAnyAuthority("NFE_EXPORTAR", "ROLE_ADMIN")
                // Todas as outras requisições requerem autenticação
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/login") // Página de login personalizada
                .defaultSuccessUrl("/dashboard", true) // Redireciona para o dashboard após login bem-sucedido
                .permitAll() // Permite acesso à página de login para todos
            )
            .logout(logout -> logout
                .logoutRequestMatcher(new AntPathRequestMatcher("/logout")) // URL para logout
                .logoutSuccessUrl("/login?logout") // Redireciona para a página de login com mensagem de logout
                .invalidateHttpSession(true) // Invalida a sessão HTTP
                .deleteCookies("JSESSIONID") // Deleta o cookie de sessão
                .permitAll() // Permite acesso ao logout para todos
            );
        return http.build();
    }
}
