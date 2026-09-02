package com.AI_knowledge.Assistant.auth.jwt;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseCookie;
import org.springframework.stereotype.Service;

import java.time.Duration;

@Service
public class JwtCookieService {

    @Value("${jwt.cookie_name}")
    private String cookieName;

    @Value("${jwt.cookie_secure}")
    private boolean secure;

    // create auth cookie
    public ResponseCookie generateJwtCookie(String token) {

        return ResponseCookie.from(cookieName, token)
                .httpOnly(true)
                .secure(secure)
                .path("/")
                .sameSite("Strict")
                .maxAge(Duration.ofDays(1))
                .build();
    }

    // clear auth cookie
    public ResponseCookie clearJwtCookie() {

        return ResponseCookie.from(cookieName, "")
                .httpOnly(true)
                .secure(secure)
                .path("/")
                .sameSite("Strict")
                .maxAge(0)
                .build();
    }
}
