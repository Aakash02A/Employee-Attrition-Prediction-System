package com.eaps.backend.security;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.Test;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.Date;

import static org.junit.jupiter.api.Assertions.*;

class JwtUtilTest {

    private final JwtUtil jwtUtil = new JwtUtil();
    private final String secret = "eaps-very-secure-secret-key-that-must-be-long-enough-for-hs256";

    private SecretKey getSigningKey() {
        return Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
    }

    @Test
    void testGenerateTokenAndExtractUsername() {
        UserDetails userDetails = new User("admin@eaps.com", "password", Collections.emptyList());

        String token = jwtUtil.generateToken(userDetails);
        assertNotNull(token);
        assertFalse(token.isEmpty());

        String username = jwtUtil.extractUsername(token);
        assertEquals("admin@eaps.com", username);
    }

    @Test
    void testValidateValidToken() {
        UserDetails userDetails = new User("admin@eaps.com", "password", Collections.emptyList());
        String token = jwtUtil.generateToken(userDetails);

        boolean isValid = jwtUtil.validateToken(token, userDetails);
        assertTrue(isValid);
    }

    @Test
    void testValidateTokenWithDifferentUser() {
        UserDetails userDetails1 = new User("admin@eaps.com", "password", Collections.emptyList());
        UserDetails userDetails2 = new User("other@eaps.com", "password", Collections.emptyList());

        String token = jwtUtil.generateToken(userDetails1);
        boolean isValid = jwtUtil.validateToken(token, userDetails2);
        assertFalse(isValid);
    }

    @Test
    void testExpiredTokenValidationFails() {
        // Construct an explicitly expired JWT (issued 2 hours ago, expired 1 hour ago)
        String expiredToken = Jwts.builder()
                .subject("admin@eaps.com")
                .issuedAt(new Date(System.currentTimeMillis() - 7200000L))
                .expiration(new Date(System.currentTimeMillis() - 3600000L))
                .signWith(getSigningKey())
                .compact();

        UserDetails userDetails = new User("admin@eaps.com", "password", Collections.emptyList());
        assertThrows(Exception.class, () -> jwtUtil.validateToken(expiredToken, userDetails));
    }

    @Test
    void testTamperedTokenFailsValidation() {
        UserDetails userDetails = new User("admin@eaps.com", "password", Collections.emptyList());
        String token = jwtUtil.generateToken(userDetails);
        String tamperedToken = token + "corrupted";

        assertThrows(Exception.class, () -> jwtUtil.validateToken(tamperedToken, userDetails));
    }
}
