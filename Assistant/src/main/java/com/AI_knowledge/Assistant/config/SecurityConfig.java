package com.AI_knowledge.Assistant.config;

import com.AI_knowledge.Assistant.auth.security.AuthEntryPointJwt;
import com.AI_knowledge.Assistant.auth.security.AuthTokenFilter;
import com.AI_knowledge.Assistant.auth.security.UserDetailsServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.web.csrf.CookieCsrfTokenRepository;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    @Autowired
    private AuthEntryPointJwt unauthorizedHandler;

    @Autowired
    private AuthTokenFilter authTokenFilter;

    @Autowired
    private UserDetailsServiceImpl userDetailsService;

    // password encoder
    @Bean
    public PasswordEncoder passwordEncoder(){
        return new BCryptPasswordEncoder();
    }

    // authenticatnion manager
    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration authConfig) throws  Exception{
        return authConfig.getAuthenticationManager();
    }

    // core security config
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception{
        http

                .cors(cors -> {})

                // disable csrf (since using jwt)
                .csrf(csrf -> csrf.disable()
                )

                // no session (stateless)
                .sessionManagement(session->
                        session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))

                // exception handling
                .exceptionHandling(ex->
                        ex.authenticationEntryPoint(unauthorizedHandler))

                // endpoint rules
                .authorizeHttpRequests(auth->auth
//                        .requestMatchers("/auth/**").permitAll()
                                .requestMatchers(
                                        "/auth/login",
                                        "/auth/signup"
                                ).permitAll()
                                .anyRequest().authenticated()
                );

        // add jwt filter before spring auth filter
        http.addFilterBefore(authTokenFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}
