package com.AI_knowledge.Assistant.auth.security;

import com.AI_knowledge.Assistant.model.User;
import lombok.Getter;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.List;
import java.util.Objects;

public class UserDetailsImpl implements UserDetails {

    // getters and setters
    @Getter
    private Long id;
    private String email;
    private String password;
    private Boolean isActive;

    // a collection to store the user authorities - roles
    private Collection<? extends GrantedAuthority> authorities;


    // constructor to set all the variables
    public UserDetailsImpl(Long id, String email, String password, Collection<? extends GrantedAuthority> authorities,Boolean isActive) {
        this.id = id;
        this.email = email;
        this.password = password;
        this.authorities = authorities;
        this.isActive = isActive;
    }


    // static constructor
    public static UserDetailsImpl build(User user){
        List<GrantedAuthority> authorities = List.of(
                new SimpleGrantedAuthority(user.getRole() != null ? user.getRole().name() : "ROLE_USER")
        );

        return new UserDetailsImpl(
                user.getId(),
                user.getEmail(),
                user.getPassword(),
                authorities,
                user.getIsActive()
        );
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return authorities;
    }

    @Override
    public String getPassword() {
        return password;
    }

    @Override
    public String getUsername() {
        return email; // since we are using email for username
    }

    // 🔒 Account flags (keep true for now)
    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        return true;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        return Boolean.TRUE.equals(isActive);
    }

    // 🔥 Important for equality checks in security context
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof UserDetailsImpl)) return false;
        UserDetailsImpl that = (UserDetailsImpl) o;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

}
