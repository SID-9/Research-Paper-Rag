package com.AI_knowledge.Assistant.auth.controller;

import com.AI_knowledge.Assistant.auth.dto.*;
import com.AI_knowledge.Assistant.auth.jwt.JwtCookieService;
import com.AI_knowledge.Assistant.auth.security.UserDetailsImpl;
import com.AI_knowledge.Assistant.auth.service.AuthService;
import com.AI_knowledge.Assistant.model.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseCookie;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/auth")
public class AuthController {

    @Autowired
    private AuthService authService;

    @Autowired
    private JwtCookieService jwtCookieService;

    // LOGIN
    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(@RequestBody LoginRequest request) {

        String token = authService.login(
                request.getEmail(),
                request.getPassword()
        );

        ResponseCookie jwtCookie =
                jwtCookieService.generateJwtCookie(token);

        LoginResponse dto = new LoginResponse("Login Successful");

        return ResponseEntity.ok()
                .header(HttpHeaders.SET_COOKIE, jwtCookie.toString())
                .body(dto);
    }

    //  SIGNUP
    @PostMapping("/signup")
    public ResponseEntity<SignupResponse> signup(@RequestBody SignupRequest request) {

        User user = authService.register(
                request.getEmail(),
                request.getPassword()
        );

        SignupResponse dto = new SignupResponse("User registered successfully");

        return ResponseEntity.ok(dto);
    }

    //  LOGOUT
    @PostMapping("/logout")
    public ResponseEntity<MessageResponse> logout() {

        ResponseCookie cleanCookie =
                jwtCookieService.clearJwtCookie();

        MessageResponse dto = new MessageResponse("Logged out successfully");

        return ResponseEntity.ok()
                .header(HttpHeaders.SET_COOKIE, cleanCookie.toString())
                .body(dto);
    }

    @GetMapping("/me")
    public ResponseEntity<UserResponse> currentUser(Authentication authentication) {

        UserDetailsImpl userDetails =
                (UserDetailsImpl) authentication.getPrincipal();

        UserResponse dto = new UserResponse(
                userDetails.getId(),
                userDetails.getUsername(),
                "USER"
        );

        return ResponseEntity.ok(dto);
    }


}
