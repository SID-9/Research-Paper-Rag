package com.AI_knowledge.Assistant.auth.service;


import com.AI_knowledge.Assistant.auth.jwt.JwtUtils;
import com.AI_knowledge.Assistant.auth.security.UserDetailsImpl;
import com.AI_knowledge.Assistant.enums.Role;
import com.AI_knowledge.Assistant.exception.EmailAlreadyExistsException;
import com.AI_knowledge.Assistant.model.User;
import com.AI_knowledge.Assistant.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.*;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private JwtUtils jwtUtils;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    // 🔐 LOGIN
    public String login(String email, String password) {

        // if authentication fails → exception thrown automatically
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(email, password)
        );
        return jwtUtils.generateJwtToken(email);




    }

    // 📝 SIGNUP
    public User register(String email, String password) {

        if (userRepository.existsByEmail(email)) {
            throw new EmailAlreadyExistsException("Email already in use");
        }

        User user = new User();
        user.setEmail(email);
        user.setPassword(passwordEncoder.encode(password));

        // 🔥 default role
        user.setRole(Role.ROLE_USER); // adjust based on your enum

        return userRepository.save(user);
    }
}