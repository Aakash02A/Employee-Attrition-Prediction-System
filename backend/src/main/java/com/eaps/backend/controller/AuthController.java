package com.eaps.backend.controller;

import com.eaps.backend.dto.AuthRequest;
import com.eaps.backend.dto.AuthResponse;
import com.eaps.backend.model.AppUser;
import com.eaps.backend.repository.AppUserRepository;
import com.eaps.backend.security.JwtUtil;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final JwtUtil jwtUtil;
    private final AppUserRepository appUserRepository;

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody AuthRequest request) {
        // Authenticate using the AuthenticationManager
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getEmail(), request.getPassword())
        );

        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        AppUser appUser = appUserRepository.findByEmail(request.getEmail()).orElseThrow();

        // Generate JWT token
        String token = jwtUtil.generateToken(userDetails);

        // Return AuthResponse
        return ResponseEntity.ok(AuthResponse.builder()
                .token(token)
                .role(appUser.getRole().name())
                .fullName(appUser.getUsername()) // AppUser's username field contains the full_name
                .build());
    }
}
