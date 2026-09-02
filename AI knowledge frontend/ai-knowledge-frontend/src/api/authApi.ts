import api from "./axios";

import type {
    LoginRequest,
    SignupRequest,
    User,
    LoginResponse,
    SignupResponse,
    LogoutResponse
} from "../types/auth";

/**
 * Authentication API
 *
 * Responsible only for communicating
 * with the Spring Boot authentication endpoints.
 */
const authApi = {

    /**
     * Login user.
     */
    async login(
        email: string,
        password: string
    ): Promise<LoginResponse> {

        const loginRequest: LoginRequest = {
            email,
            password,
        };

        const response = await api.post<LoginResponse>(
            "/auth/login",
            loginRequest
        );

        return response.data;
    },

    /**
     * Register user.
     */
    async signup(
        email: string,
        password: string
    ): Promise<SignupResponse> {

        const signupRequest: SignupRequest = {
            email,
            password,
        };

        const response = await api.post<SignupResponse>(
            "/auth/signup",
            signupRequest
        );

        return response.data;
    },

    /**
     * Logout user.
     */
    async logout(): Promise<LogoutResponse> {

       const response =  await api.post<LogoutResponse>("/auth/logout");
       return response.data;

    },

    /**
     * Returns the currently authenticated user.
     */
    async getCurrentUser(): Promise<User> {

        const response = await api.get<User>("/auth/me");

        return response.data;

    },

};

export default authApi;


//===================================================
// import api from "./axios";

// import type{
//     LoginRequest,
//     SignupRequest,
//     User,
//     SignupResponse,
//     LoginResponse,
//     LogoutResponse
// }from "../types/auth";

// /**
//  * Authentication API
//  *
//  * This file contains every HTTP request related
//  * to authentication.
//  *
//  * Components should NEVER call Axios directly.
//  * They should only call these methods.
//  */


// const authAPi = {
//     /**
//      * Login user.
//      *
//      * Spring Boot:
//      * POST /auth/login
//      *
//      * Response:
//      * - Sets HttpOnly JWT Cookie
//      * - Returns "Login successful"
//      */

//     async login(loginRequest: LoginRequest): Promise<LoginResponse>{
//         const response = await api.post<LoginResponse>("/auth/login",loginRequest);
//         return response.data;
//     },
//      /**
//      * Register a new user.
//      *
//      * Spring Boot:
//      * POST /auth/signup
//      */

//      async signup(signupRequest: SignupRequest): Promise<SignupResponse>{
//         const response = await api.post<SignupResponse>("/auth/signup",signupRequest);
//         return response.data;
//      },

//      /**
//      * Logout user.
//      *
//      * Spring Boot clears the HttpOnly cookie.
//      */

//      async logout(): Promise<LogoutResponse>{
//         const response = await api.post<LogoutResponse>("/auth/logout");
//         return response.data;
//      },
//       /**
//      * Returns the currently authenticated user.
//      *
//      * GET /auth/me
//      */

//       async getCurrentUser(): Promise<User>{
//         const response = await api.get<User>("/auth/me");
//         return response.data;
//       }

// }