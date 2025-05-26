package com.exemplo.nfe.controller;

import com.exemplo.nfe.model.EPapel;
import com.exemplo.nfe.model.Papel;
import com.exemplo.nfe.model.Usuario;
import com.exemplo.nfe.repository.PapelRepository;
import com.exemplo.nfe.repository.UsuarioRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * Controlador REST para gerenciamento de usuários.
 * Apenas usuários com o papel 'ADMIN' podem acessar estes endpoints.
 */
@RestController
@RequestMapping("/api/admin/users")
@PreAuthorize("hasRole('ADMIN')") // Protege todos os métodos deste controlador para o papel ADMIN
@Tag(name = "Gerenciamento de Usuários (Admin)", description = "APIs para operações CRUD de usuários, restrito a administradores")
public class AdminUserController {

    @Autowired
    private UsuarioRepository usuarioRepository;

    @Autowired
    private PapelRepository papelRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    /**
     * Lista todos os usuários cadastrados.
     * @return Uma lista de objetos Usuario.
     */
    @Operation(summary = "Listar todos os usuários")
    @GetMapping
    public ResponseEntity<List<Usuario>> getAllUsers() {
        List<Usuario> users = usuarioRepository.findAll();
        return ResponseEntity.ok(users);
    }

    /**
     * Busca um usuário pelo ID.
     * @param id O ID do usuário.
     * @return O usuário encontrado ou 404 Not Found.
     */
    @Operation(summary = "Obter usuário por ID")
    @GetMapping("/{id}")
    public ResponseEntity<Usuario> getUserById(@PathVariable Long id) {
        Optional<Usuario> user = usuarioRepository.findById(id);
        return user.map(ResponseEntity::ok).orElseGet(() -> ResponseEntity.notFound().build());
    }

    /**
     * Cria um novo usuário.
     * A senha é codificada antes de ser salva.
     * Os papéis devem ser passados como uma lista de strings (nomes dos papéis).
     * @param newUser O objeto Usuario a ser criado.
     * @param roleNames Nomes dos papéis a serem atribuídos ao usuário.
     * @return O usuário criado com status 201 Created.
     */
    @Operation(summary = "Criar um novo usuário",
               description = "A senha será codificada. Papéis devem ser passados como um array de strings (ex: [\"ADMIN\", \"OPERACIONAL\"]).")
    @PostMapping
    public ResponseEntity<Usuario> createUser(@RequestBody Usuario newUser,
                                              @RequestParam(required = false) List<String> roleNames) {
        if (usuarioRepository.findByEmail(newUser.getEmail()).isPresent() ||
            usuarioRepository.findByUsername(newUser.getUsername()).isPresent()) {
            return ResponseEntity.status(HttpStatus.CONFLICT).build(); // Usuário ou email já existe
        }

        newUser.setSenha(passwordEncoder.encode(newUser.getSenha())); // Codifica a senha

        if (roleNames != null && !roleNames.isEmpty()) {
            Set<Papel> papeis = new HashSet<>();
            for (String roleName : roleNames) {
                try {
                    EPapel ePapel = EPapel.valueOf(roleName.toUpperCase());
                    papelRepository.findByNome(ePapel).ifPresentOrElse(
                        papeis::add,
                        () -> {
                            Papel novoPapel = new Papel();
                            novoPapel.setNome(ePapel);
                            papeis.add(papelRepository.save(novoPapel));
                        }
                    );
                } catch (IllegalArgumentException e) {
                    System.err.println("Papel inválido fornecido: " + roleName);
                    // Opcional: retornar um erro ao cliente sobre papel inválido
                }
            }
            newUser.setPapeis(papeis);
        } else {
            // Se nenhum papel for especificado, atribui o papel padrão 'USUARIO' (ou 'OPERACIONAL')
            papelRepository.findByNome(EPapel.USUARIO).ifPresent(p -> {
                Set<Papel> defaultRoles = new HashSet<>();
                defaultRoles.add(p);
                newUser.setPapeis(defaultRoles);
            });
        }

        Usuario savedUser = usuarioRepository.save(newUser);
        return ResponseEntity.status(HttpStatus.CREATED).body(savedUser);
    }

    /**
     * Atualiza um usuário existente.
     * @param id O ID do usuário a ser atualizado.
     * @param updatedUser O objeto Usuario com os dados atualizados.
     * @param roleNames Nomes dos papéis a serem atribuídos ao usuário.
     * @return O usuário atualizado ou 404 Not Found.
     */
    @Operation(summary = "Atualizar um usuário existente",
               description = "A senha será atualizada apenas se um novo valor for fornecido. Papéis podem ser atualizados.")
    @PutMapping("/{id}")
    public ResponseEntity<Usuario> updateUser(@PathVariable Long id,
                                              @RequestBody Usuario updatedUser,
                                              @RequestParam(required = false) List<String> roleNames) {
        return usuarioRepository.findById(id).map(user -> {
            user.setUsername(updatedUser.getUsername());
            user.setEmail(updatedUser.getEmail());
            user.setEnabled(updatedUser.isEnabled());

            if (updatedUser.getSenha() != null && !updatedUser.getSenha().isEmpty()) {
                user.setSenha(passwordEncoder.encode(updatedUser.getSenha())); // Codifica a nova senha
            }

            if (roleNames != null) { // Se roleNames for nulo, não altera os papéis existentes
                Set<Papel> newPapeis = new HashSet<>();
                for (String roleName : roleNames) {
                    try {
                        EPapel ePapel = EPapel.valueOf(roleName.toUpperCase());
                        papelRepository.findByNome(ePapel).ifPresentOrElse(
                            newPapeis::add,
                            () -> {
                                Papel novoPapel = new Papel();
                                novoPapel.setNome(ePapel);
                                newPapeis.add(papelRepository.save(novoPapel));
                            }
                        );
                    } catch (IllegalArgumentException e) {
                        System.err.println("Papel inválido fornecido: " + roleName);
                    }
                }
                user.setPapeis(newPapeis);
            }

            Usuario savedUser = usuarioRepository.save(user);
            return ResponseEntity.ok(savedUser);
        }).orElseGet(() -> ResponseEntity.notFound().build());
    }

    /**
     * Exclui um usuário pelo ID.
     * @param id O ID do usuário a ser excluído.
     * @return Status 204 No Content se bem-sucedido.
     */
    @Operation(summary = "Excluir um usuário por ID")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        if (!usuarioRepository.existsById(id)) {
            return ResponseEntity.notFound().build();
        }
        usuarioRepository.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}
