import axios from "axios";

/**
 * Shared Axios instance used throughout the application.
 *
 * Why?
 * ----
 * Instead of configuring Axios in every component,
 * we configure it once here.
 *
 * Every API module (auth, documents, chat, etc.)
 * will use this instance.
 */
console.log(import.meta.env.VITE_API_BASE_URL);
const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,

    /**
     * Automatically include HttpOnly cookies
     * with every request.
     *
     * This is REQUIRED because our Spring Boot
     * authentication uses Cookie JWT.
     */
    withCredentials: true,

    /**
     * Default JSON content type.
     *
     * Axios automatically changes this when sending
     * FormData (like PDF uploads), so we don't need
     * to worry about upload requests later.
     */
    headers: {
        "Content-Type": "application/json",
    },
    
});

export default api;