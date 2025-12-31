package com.timeweaver.usermanagement.web;

import com.timeweaver.usermanagement.model.User;
import com.timeweaver.usermanagement.repo.UserRepository;
import com.timeweaver.usermanagement.security.TokenService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.net.URI;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@SuppressWarnings("null")
public class AuthController {

    private final UserRepository users;
    private final PasswordEncoder encoder;
    private final TokenService tokens;

    public AuthController(UserRepository users, PasswordEncoder encoder, TokenService tokens) {
        this.users = users;
        this.encoder = encoder;
        this.tokens = tokens;
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody RegisterRequest req) {
        if (req.email == null || req.email.isBlank()) {
            return ResponseEntity.badRequest().body(Map.of("error", "email_required"));
        }
        if (req.password == null || req.password.length() < 6) {
            return ResponseEntity.badRequest().body(Map.of("error", "password_too_short"));
        }
        if (users.existsByEmail(req.email)) {
            return ResponseEntity.badRequest().body(Map.of("error", "email_exists"));
        }
        User u = new User();
        u.setName(req.name != null ? req.name : req.email.split("@")[0]);
        u.setEmail(req.email);
        u.setPasswordHash(encoder.encode(req.password));
        u.setRole(req.role == null ? "USER" : req.role.toUpperCase());
        User saved = users.save(u);
        String token = tokens.generateToken(saved.getEmail(), saved.getRole(), Map.of("uid", saved.getId()));
        if (saved.getId() == null)
            throw new IllegalStateException("Saved user has no ID");
        return ResponseEntity.created(URI.create("/api/users/" + saved.getId()))
                .body(Map.of("token", token, "user", Map.of("id", saved.getId(), "email", saved.getEmail(), "name",
                        saved.getName(), "role", saved.getRole())));
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest req) {
        if (req.email == null || req.password == null) {
            return ResponseEntity.badRequest().body(Map.of("error", "email_and_password_required"));
        }
        return users.findByEmail(req.email)
                .filter(u -> encoder.matches(req.password, u.getPasswordHash()))
                .<ResponseEntity<?>>map(u -> {
                    String token = tokens.generateToken(u.getEmail(), u.getRole(), Map.of("uid", u.getId()));
                    return ResponseEntity.ok(Map.of("token", token, "user",
                            Map.of("id", u.getId(), "email", u.getEmail(), "name", u.getName(), "role", u.getRole())));
                })
                .orElse(ResponseEntity.status(401).body(Map.of("error", "invalid_credentials")));
    }

    @PostMapping("/validate")
    public ResponseEntity<?> validateToken(@RequestBody ValidateTokenRequest req) {
        if (req.token == null || req.token.isBlank()) {
            return ResponseEntity.badRequest().body(Map.of("valid", false, "error", "token_required"));
        }
        try {
            if (tokens.validateToken(req.token)) {
                String email = tokens.getEmailFromToken(req.token);
                String role = tokens.getRoleFromToken(req.token);
                Long uid = tokens.getUserIdFromToken(req.token);
                return ResponseEntity.ok(Map.of(
                        "valid", true,
                        "email", email,
                        "role", role,
                        "uid", uid != null ? uid : ""
                ));
            } else {
                return ResponseEntity.ok(Map.of("valid", false, "error", "invalid_token"));
            }
        } catch (Exception e) {
            return ResponseEntity.ok(Map.of("valid", false, "error", "token_validation_failed"));
        }
    }

    @PostMapping("/refresh")
    public ResponseEntity<?> refreshToken(@RequestBody RefreshTokenRequest req) {
        if (req.token == null || req.token.isBlank()) {
            return ResponseEntity.badRequest().body(Map.of("error", "token_required"));
        }
        try {
            if (tokens.validateToken(req.token)) {
                String email = tokens.getEmailFromToken(req.token);
                
                // Vérifier que l'utilisateur existe toujours
                return users.findByEmail(email)
                        .<ResponseEntity<?>>map(u -> {
                            String newToken = tokens.generateToken(u.getEmail(), u.getRole(), Map.of("uid", u.getId()));
                            return ResponseEntity.ok(Map.of(
                                    "token", newToken,
                                    "user", Map.of(
                                            "id", u.getId(),
                                            "email", u.getEmail(),
                                            "name", u.getName(),
                                            "role", u.getRole()
                                    )
                            ));
                        })
                        .orElse(ResponseEntity.status(401).body(Map.of("error", "user_not_found")));
            } else {
                return ResponseEntity.status(401).body(Map.of("error", "invalid_token"));
            }
        } catch (Exception e) {
            return ResponseEntity.status(401).body(Map.of("error", "token_validation_failed"));
        }
    }

    public static class RegisterRequest {
        public String name;
        public String email;
        public String password;
        public String role; // optional
    }

    public static class LoginRequest {
        public String email;
        public String password;
    }

    public static class ValidateTokenRequest {
        public String token;
    }

    public static class RefreshTokenRequest {
        public String token;
    }
}
