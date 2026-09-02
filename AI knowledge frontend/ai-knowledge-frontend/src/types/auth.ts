// ==========================================================
// Authentication Types
// ==========================================================

/**
 * Represents the authenticated user returned
 * by Spring Boot.
 *
 * Mirrors the UserResponseDto returned from:
 *
 * GET /auth/me
 */


export interface User{
     id: number;
     email: string;
     role: string;
}
/**
 * Login request body.
 *
 * POST /auth/login
 */
export interface LoginRequest{
    email: string;
    password: string;
}

// login response 
export interface LoginResponse{
    message: string;
}

/**
 * Signup request body.
 *
 * POST /auth/signup
 */
export interface SignupRequest{
    email: string;
    password: string;
}

// signup response body
export interface SignupResponse{
    message: string;
}

export interface LogoutResponse{
    message: string;
}