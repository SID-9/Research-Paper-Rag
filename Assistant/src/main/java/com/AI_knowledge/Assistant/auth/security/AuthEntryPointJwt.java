package com.AI_knowledge.Assistant.auth.security;

import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.stereotype.Component;

import java.io.IOException;

@Component
public class AuthEntryPointJwt implements AuthenticationEntryPoint {

    @Override
    public void commence(HttpServletRequest request,
                         HttpServletResponse response,
                         AuthenticationException authException)
            throws IOException, ServletException {

        response.setContentType("application/json");
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);

        String jsonResponse = String.format(
                "{ \"status\": %d, \"error\": \"Unauthorized\", \"message\": \"%s\", \"path\": \"%s\" }",
                HttpServletResponse.SC_UNAUTHORIZED,
                authException.getMessage(),
                request.getServletPath()
        );

        response.getWriter().write(jsonResponse);
    }
}
