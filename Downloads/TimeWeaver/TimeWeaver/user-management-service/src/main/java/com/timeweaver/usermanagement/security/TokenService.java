package com.timeweaver.usermanagement.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Date;
import java.util.Map;

@Service
public class TokenService {
    private final SecretKey key;
    private final long ttlSeconds;

    public TokenService(@Value("${app.jwt.secret}") String secret,
                        @Value("${app.jwt.ttlSeconds:36000}") long ttlSeconds) {
        // Utiliser la clé secrète directement pour créer une SecretKey
        byte[] keyBytes = secret.getBytes(StandardCharsets.UTF_8);
        // S'assurer que la clé fait au moins 256 bits (32 bytes) pour HS256
        if (keyBytes.length < 32) {
            byte[] paddedKey = new byte[32];
            System.arraycopy(keyBytes, 0, paddedKey, 0, Math.min(keyBytes.length, 32));
            this.key = Keys.hmacShaKeyFor(paddedKey);
        } else {
            this.key = Keys.hmacShaKeyFor(keyBytes);
        }
        this.ttlSeconds = ttlSeconds;
    }

    public String generateToken(String subject, String role, Map<String, Object> extra) {
        Instant now = Instant.now();
        var builder = Jwts.builder()
                .setSubject(subject)
                .setIssuedAt(Date.from(now))
                .setExpiration(Date.from(now.plusSeconds(ttlSeconds)))
                .claim("role", role);
        
        if (extra != null) {
            for (Map.Entry<String, Object> entry : extra.entrySet()) {
                builder.claim(entry.getKey(), entry.getValue());
            }
        }
        
        return builder.signWith(key).compact();
    }

    public Claims parseToken(String token) throws JwtException {
        return Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    public boolean validateToken(String token) {
        try {
            parseToken(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    public String getEmailFromToken(String token) {
        Claims claims = parseToken(token);
        return claims.getSubject();
    }

    public String getRoleFromToken(String token) {
        Claims claims = parseToken(token);
        return claims.get("role", String.class);
    }

    public Long getUserIdFromToken(String token) {
        Claims claims = parseToken(token);
        Object uid = claims.get("uid");
        if (uid instanceof Number) {
            return ((Number) uid).longValue();
        }
        return null;
    }
}
