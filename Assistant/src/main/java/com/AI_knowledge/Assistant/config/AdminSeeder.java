package com.AI_knowledge.Assistant.config;

import com.AI_knowledge.Assistant.enums.Role;
import com.AI_knowledge.Assistant.model.User;
import com.AI_knowledge.Assistant.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;


// THIS CLASS IS TO INITIALIZE THE FIRST EVER SUPER ADMIN FOR THE APPLICATION
// THIS ADMIN WILL MANUALLY CREATE THE STUDENT , TEACHER , OTHER ADMIN DETAILS
// SO THAT THE OTHER PEOPLE CAN ACCESS THEIR PROFILES AND LOGIN / COMPLETE THEM LATER
@Component
public class AdminSeeder implements CommandLineRunner {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Value("${app.admin.email}")
    private String email;

    @Value("${app.admin.password}")
    private String password;

    @Override
    public void run(String... args) {

        if (!userRepository.existsByEmail(email)) {

            User admin = new User();

            admin.setEmail(email);

            admin.setPassword(
                    passwordEncoder.encode(password)
            );

            admin.setRole(Role.ROLE_ADMIN);

            admin.setIsActive(true);

            userRepository.save(admin);

            System.out.println("Default admin created");
        }
    }
}